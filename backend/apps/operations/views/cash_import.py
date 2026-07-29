"""
收银数据导入视图
"""
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
import pandas as pd
from io import BytesIO
import json
from datetime import datetime
from apps.operations.models import CashImportRecord, SalesRecord, SalesItem, OperationLog, InventoryTransaction
from ..serializers import CashImportRecordSerializer, CashImportSerializer
from ..permissions import CashImportPermission
from apps.products.models import Product, ProductInventory


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CashImportRecordViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """收银数据导入记录视图集"""
    queryset = CashImportRecord.objects.all()
    serializer_class = CashImportRecordSerializer
    permission_classes = [IsAuthenticated, CashImportPermission]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = super().get_queryset()
        
        import_type = self.request.query_params.get('import_type')
        if import_type:
            queryset = queryset.filter(import_type=import_type)
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload_cash_data(self, request):
        """上传收银数据"""
        serializer = CashImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file = serializer.validated_data['file']
        import_type = serializer.validated_data['import_type']
        overwrite = serializer.validated_data.get('overwrite', False)
        
        try:
            # 创建导入记录
            import_record = CashImportRecord.objects.create(
                file_name=file.name,
                file_size=file.size,
                import_type=import_type,
                status='processing',
                import_user=request.user
            )
            
            # 处理文件
            content = file.read()
            
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                # 处理Excel文件
                df = pd.read_excel(BytesIO(content))
            elif file.name.endswith('.csv'):
                # 处理CSV文件
                df = pd.read_csv(BytesIO(content))
            else:
                raise ValueError('不支持的文件格式')
            
            # 开始处理数据
            success_count = 0
            fail_count = 0
            errors = []
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        if import_type == 'sales':
                            # 处理销售数据
                            self._process_sales_row(row, request.user)
                            success_count += 1
                        else:
                            # 处理库存数据
                            self._process_inventory_row(row, request.user)
                            success_count += 1
                            
                    except Exception as e:
                        fail_count += 1
                        errors.append(f"第{index+2}行: {str(e)}")
                
                # 更新导入记录
                import_record.total_records = len(df)
                import_record.success_count = success_count
                import_record.fail_count = fail_count
                import_record.status = 'completed' if success_count > 0 else 'failed'
                if errors:
                    import_record.error_message = '\n'.join(errors[:10])  # 只保存前10个错误
                import_record.save()
            
            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,
                action_type=OperationLog.ActionType.IMPORT,
                model_name='CashImportRecord',
                object_id=str(import_record.id),
                object_repr=str(import_record),
                action_detail=f'导入收银数据: {file.name}，成功{success_count}条，失败{fail_count}条',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'message': f'数据导入完成，成功{success_count}条，失败{fail_count}条',
                'import_id': import_record.id,
                'success_count': success_count,
                'fail_count': fail_count,
                'errors': errors[:5]  # 返回前5个错误
            })
            
        except Exception as e:
            return Response(
                {'error': f'文件处理失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _process_sales_row(self, row, user):
        """处理销售数据行"""
        # 解析销售数据
        order_number = row.get('order_number', '')
        customer_name = row.get('customer_name', '')
        customer_phone = row.get('customer_phone', '')
        product_code = row.get('product_code', '')
        quantity = int(row.get('quantity', 0))
        unit_price = float(row.get('unit_price', 0))
        sales_channel = row.get('sales_channel', 'store')
        payment_method = row.get('payment_method', 'cash')
        remark = row.get('remark', '')
        
        if not order_number or not product_code or quantity <= 0:
            raise ValueError('销售数据不完整')
        
        # 查找商品
        try:
            product = Product.objects.get(code=product_code, status=1)
        except Product.DoesNotExist:
            raise ValueError(f'商品不存在: {product_code}')
        
        # 检查库存
        inventory = ProductInventory.objects.filter(
            product=product,
            warehouse__status=1
        ).first()
        
        if not inventory or inventory.available_stock < quantity:
            raise ValueError(f'库存不足: {product_code}')
        
        # 查找或创建销售记录
        sales_record, created = SalesRecord.objects.get_or_create(
            order_number=order_number,
            defaults={
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'sales_channel': sales_channel,
                'payment_method': payment_method,
                'total_amount': quantity * unit_price,
                'actual_amount': quantity * unit_price,
                'cashier': user,
                'remark': remark,
                'sales_time': datetime.now()
            }
        )

        line_amount = quantity * unit_price
        if not created:
            sales_record.total_amount += line_amount
            sales_record.actual_amount += line_amount
            if remark:
                sales_record.remark = remark
            sales_record.save(update_fields=['total_amount', 'actual_amount', 'remark', 'update_time'])
        
        # 创建销售明细
        SalesItem.objects.create(
            sales_record=sales_record,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=line_amount
        )

        InventoryTransaction.objects.create(
            transaction_type=InventoryTransaction.TransactionType.SALE_OUT,
            status=InventoryTransaction.TransactionStatus.COMPLETED,
            product=product,
            warehouse=inventory.warehouse,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=line_amount,
            related_order=order_number,
            remark=f'收银导入出库: {remark}'.strip(': ')
        )
        
        # 更新库存
        inventory.current_stock -= quantity
        inventory.save()
    
    def _process_inventory_row(self, row, user):
        """处理库存数据行"""
        # 这里可以扩展库存数据处理逻辑
        pass
    
    def perform_destroy(self, instance):
        """删除导入记录"""
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='CashImportRecord',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除收银数据导入记录',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        instance.delete()