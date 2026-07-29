"""
库存交易视图
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, F, Q
from django.db import transaction
from datetime import datetime, timedelta
from apps.operations.models import InventoryTransaction, OperationLog
from apps.products.models import ProductInventory
from ..serializers import InventoryTransactionSerializer, InventoryInOutSerializer
from ..permissions import InventoryTransactionPermission
from apps.products.models import Product, Warehouse, Supplier


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """库存交易视图集"""
    queryset = InventoryTransaction.objects.filter(status='completed')
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated, InventoryTransactionPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'status', 'product', 'warehouse', 'related_supplier']
    search_fields = ['code', 'related_order', 'remark', 'product__name']
    ordering_fields = ['transaction_time', 'quantity', 'total_amount', 'create_time']
    ordering = ['-transaction_time']
    
    def get_queryset(self):
        """根据查询参数过滤交易记录"""
        queryset = super().get_queryset().select_related('product', 'warehouse', 'related_supplier')
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(transaction_time__date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(transaction_time__date__lte=end_date)
        
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            if transaction_type == 'in':  # 所有入库类型
                queryset = queryset.filter(
                    transaction_type__in=['purchase_in', 'purchase_return', 'adjust_in']
                )
            elif transaction_type == 'out':  # 所有出库类型
                queryset = queryset.filter(
                    transaction_type__in=['sale_out', 'sale_return', 'adjust_out', 'transfer']
                )
        
        return queryset
    
    def perform_create(self, serializer):
        """创建库存交易时记录日志"""
        transaction_record = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.INVENTORY_IN 
                if transaction_record.transaction_type in ['purchase_in', 'adjust_in', 'purchase_return']
                else OperationLog.ActionType.INVENTORY_OUT,
            model_name='InventoryTransaction',
            object_id=str(transaction_record.id),
            object_repr=str(transaction_record),
            action_detail=f'创建{transaction_record.get_transaction_type_display()}交易',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        """更新库存交易时记录日志"""
        new_instance = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='InventoryTransaction',
            object_id=str(new_instance.id),
            object_repr=str(new_instance),
            action_detail='更新库存交易信息',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        """删除库存交易时记录日志"""
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='InventoryTransaction',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除库存交易',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取库存交易统计"""
        queryset = self.get_queryset()
        
        # 总交易金额
        total_amount = queryset.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # 总交易数量
        total_quantity = queryset.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        # 按交易类型统计
        type_stats = queryset.values('transaction_type').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity'),
            total_amount=Sum('total_amount')
        ).order_by('transaction_type')
        
        # 近30天交易趋势
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_transactions = queryset.filter(
            transaction_time__date__gte=thirty_days_ago
        ).values('transaction_time__date').annotate(
            daily_amount=Sum('total_amount'),
            daily_count=Count('id')
        ).order_by('transaction_time__date')
        
        # 热门商品交易统计
        product_stats = queryset.values(
            'product__name', 'product__code'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum('total_amount'),
            transaction_count=Count('id')
        ).order_by('-total_amount')[:10]
        
        return Response({
            'total_amount': float(total_amount),
            'total_quantity': total_quantity,
            'type_stats': list(type_stats),
            'recent_transactions': list(recent_transactions),
            'product_stats': list(product_stats)
        })
    
    @action(detail=False, methods=['post'])
    def inventory_in_out(self, request):
        """入库/出库操作"""
        serializer = InventoryInOutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        product_id = data['product_id']
        warehouse_id = data['warehouse_id']
        quantity = data['quantity']
        unit_price = data['unit_price']
        transaction_type = data['transaction_type']
        related_supplier_id = data.get('related_supplier_id')
        
        try:
            with transaction.atomic():
                # 获取商品和仓库
                product = Product.objects.get(id=product_id, status=1)
                warehouse = Warehouse.objects.get(id=warehouse_id, status=1)
                related_supplier = None
                if related_supplier_id:
                    related_supplier = Supplier.objects.get(id=related_supplier_id, status=1)
                
                # 获取或创建库存记录
                inventory, created = ProductInventory.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'current_stock': 0,
                        'locked_stock': 0,
                        'available_stock': 0
                    }
                )
                
                # 创建交易记录
                transaction_record = InventoryTransaction.objects.create(
                    transaction_type=transaction_type,
                    status='completed',
                    product=product,
                    warehouse=warehouse,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_amount=quantity * unit_price,
                    related_supplier=related_supplier,
                    related_order=data.get('related_order', ''),
                    remark=data.get('remark', '')
                )
                
                # 更新库存
                if transaction_type in ['purchase_in', 'adjust_in']:  # 入库类交易
                    inventory.current_stock += quantity
                elif transaction_type in ['sale_out', 'adjust_out']:  # 出库类交易
                    if inventory.available_stock < quantity:
                        raise ValueError('库存不足')
                    inventory.current_stock -= quantity
                
                inventory.save()
                
                # 记录操作日志
                OperationLog.objects.create(
                    user=request.user,
                    action_type=OperationLog.ActionType.INVENTORY_IN 
                        if transaction_type in ['purchase_in', 'adjust_in']
                        else OperationLog.ActionType.INVENTORY_OUT,
                    model_name='InventoryTransaction',
                    object_id=str(transaction_record.id),
                    object_repr=str(transaction_record),
                    action_detail=f'{transaction_type}操作: {product.name} x{quantity}',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return Response(
                    InventoryTransactionSerializer(transaction_record).data,
                    status=status.HTTP_201_CREATED
                )
                
        except Product.DoesNotExist:
            return Response(
                {'error': '商品不存在或已停用'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Warehouse.DoesNotExist:
            return Response(
                {'error': '仓库不存在或已停用'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Supplier.DoesNotExist:
            return Response(
                {'error': '供货商不存在或已停用'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'操作失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def inventory_summary(self, request):
        """库存汇总统计"""
        # 获取所有商品的库存信息
        inventories = ProductInventory.objects.select_related('product', 'warehouse').all()
        
        # 统计库存金额
        inventory_value = 0
        for inv in inventories:
            inventory_value += inv.current_stock * inv.product.purchase_price
        
        # 库存预警商品
        low_stock_products = []
        for inv in inventories:
            if inv.available_stock < inv.product.min_stock:
                low_stock_products.append({
                    'product_id': inv.product.id,
                    'product_name': inv.product.name,
                    'warehouse_name': inv.warehouse.name,
                    'current_stock': inv.current_stock,
                    'min_stock': inv.product.min_stock,
                    'warning_level': 'low'
                })
        
        # 库存商品总数
        total_products = inventories.values('product').distinct().count()
        
        # 库存占用仓库数
        total_warehouses = inventories.values('warehouse').distinct().count()
        
        return Response({
            'inventory_value': float(inventory_value),
            'total_products': total_products,
            'total_warehouses': total_warehouses,
            'low_stock_warnings': len(low_stock_products),
            'low_stock_products': low_stock_products[:10]  # 只显示前10个
        })