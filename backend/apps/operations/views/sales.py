"""
销售记录视图
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, F, Q, DecimalField, ExpressionWrapper
from django.db import transaction
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from apps.operations.models import SalesRecord, SalesItem, OperationLog
from ..serializers import SalesRecordSerializer, SalesQuerySerializer, SalesItemSerializer
from ..permissions import SalesRecordPermission
from apps.products.models import Product, ProductInventory


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SalesRecordViewSet(viewsets.ModelViewSet):
    """销售记录视图集"""
    queryset = SalesRecord.objects.all()
    serializer_class = SalesRecordSerializer
    permission_classes = [IsAuthenticated, SalesRecordPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sales_channel', 'payment_method', 'cashier']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'remark']
    ordering_fields = ['sales_time', 'total_amount', 'actual_amount', 'create_time']
    ordering = ['-sales_time']
    
    def get_queryset(self):
        """根据查询参数过滤销售记录"""
        queryset = super().get_queryset().select_related('cashier')
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(sales_time__date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(sales_time__date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        """创建销售记录"""
        sales_record = serializer.save(cashier=self.request.user)
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.SALE,
            model_name='SalesRecord',
            object_id=str(sales_record.id),
            object_repr=str(sales_record),
            action_detail=f'创建销售订单: {sales_record.order_number}',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        """更新销售记录"""
        new_instance = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='SalesRecord',
            object_id=str(new_instance.id),
            object_repr=str(new_instance),
            action_detail='更新销售记录信息',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        """删除销售记录"""
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='SalesRecord',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除销售记录',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        instance.delete()
    
    @action(detail=False, methods=['post'])
    def create_with_items(self, request):
        """创建销售记录（包含商品明细）"""
        order_data = request.data.get('order', {})
        items_data = request.data.get('items', [])
        
        if not items_data:
            return Response(
                {'error': '销售明细不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # 生成订单号
                order_number = order_data.get('order_number')
                if not order_number:
                    order_number = f"SALE{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
                
                # 计算总金额
                total_amount = Decimal(0)
                for item in items_data:
                    quantity = Decimal(item.get('quantity', 0))
                    unit_price = Decimal(item.get('unit_price', 0))
                    total_amount += quantity * unit_price
                
                # 计算实收金额
                discount_amount = Decimal(order_data.get('discount_amount', 0))
                actual_amount = total_amount - discount_amount
                if actual_amount < 0:
                    actual_amount = Decimal(0)
                
                # 创建销售记录
                sales_record = SalesRecord.objects.create(
                    order_number=order_number,
                    customer_name=order_data.get('customer_name', ''),
                    customer_phone=order_data.get('customer_phone', ''),
                    sales_channel=order_data.get('sales_channel', 'store'),
                    payment_method=order_data.get('payment_method', 'cash'),
                    total_amount=total_amount,
                    discount_amount=discount_amount,
                    actual_amount=actual_amount,
                    cashier=request.user,
                    remark=order_data.get('remark', ''),
                    sales_time=order_data.get('sales_time', datetime.now())
                )
                
                # 创建销售明细并扣减库存
                sales_items = []
                for item in items_data:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity')
                    unit_price = item.get('unit_price')
                    
                    product = Product.objects.get(id=product_id, status=1)
                    
                    # 检查库存
                    inventory = ProductInventory.objects.get(
                        product=product,
                        warehouse__status=1
                    )
                    
                    if inventory.available_stock < quantity:
                        raise ValueError(f'商品 {product.name} 库存不足')
                    
                    # 创建销售明细
                    sales_item = SalesItem.objects.create(
                        sales_record=sales_record,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        subtotal=quantity * unit_price
                    )
                    
                    # 扣减库存
                    inventory.current_stock -= quantity
                    inventory.save()
                    
                    sales_items.append(sales_item)
                
                # 记录操作日志
                OperationLog.objects.create(
                    user=request.user,
                    action_type=OperationLog.ActionType.SALE,
                    model_name='SalesRecord',
                    object_id=str(sales_record.id),
                    object_repr=str(sales_record),
                    action_detail=f'完成销售订单: {order_number}，包含{len(sales_items)}个商品',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                serializer = self.get_serializer(sales_record)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Product.DoesNotExist:
            return Response(
                {'error': '商品不存在或已停用'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ProductInventory.DoesNotExist:
            return Response(
                {'error': '商品库存记录不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'创建销售记录失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def search_sales(self, request):
        """销售记录高级搜索"""
        serializer = SalesQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        start_date = data['start_date']
        end_date = data['end_date']
        sales_channel = data.get('sales_channel')
        payment_method = data.get('payment_method')
        group_by = data.get('group_by', 'day')
        
        # 基本查询
        queryset = SalesRecord.objects.filter(
            sales_time__date__gte=start_date,
            sales_time__date__lte=end_date
        )
        
        if sales_channel:
            queryset = queryset.filter(sales_channel=sales_channel)
        
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # 分组统计
        if group_by == 'day':
            stats = queryset.values('sales_time__date').annotate(
                total_sales=Sum('actual_amount'),
                order_count=Count('id'),
                avg_amount=Avg('actual_amount')
            ).order_by('sales_time__date')
        elif group_by == 'product':
            stats = SalesItem.objects.filter(
                sales_record__sales_time__date__gte=start_date,
                sales_record__sales_time__date__lte=end_date
            ).values('product__name', 'product__code').annotate(
                total_quantity=Sum('quantity'),
                total_amount=Sum('subtotal'),
                sale_count=Count('sales_record')
            ).order_by('-total_amount')
        else:
            stats = []
        
        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'filters': {
                'sales_channel': sales_channel,
                'payment_method': payment_method
            },
            'statistics': list(stats)
        })
    
    @action(detail=False, methods=['get'])
    def sales_statistics(self, request):
        """销售统计"""
        gross_profit_expr = ExpressionWrapper(
            F('subtotal') - (F('quantity') * F('product__purchase_price')),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )

        # 今日销售额
        today = datetime.now().date()
        today_sales = SalesRecord.objects.filter(
            sales_time__date=today
        ).aggregate(
            total=Sum('actual_amount')
        )['total'] or Decimal(0)
        
        # 昨日销售额
        yesterday = today - timedelta(days=1)
        yesterday_sales = SalesRecord.objects.filter(
            sales_time__date=yesterday
        ).aggregate(
            total=Sum('actual_amount')
        )['total'] or Decimal(0)
        
        # 本月销售额
        first_day_of_month = today.replace(day=1)
        month_sales = SalesRecord.objects.filter(
            sales_time__date__gte=first_day_of_month
        ).aggregate(
            total=Sum('actual_amount')
        )['total'] or Decimal(0)
        
        # 总订单数
        total_orders = SalesRecord.objects.count()
        
        # 平均订单金额
        avg_order_amount = SalesRecord.objects.aggregate(
            avg=Avg('actual_amount')
        )['avg'] or Decimal(0)
        
        # 销售渠道统计
        channel_stats = SalesRecord.objects.values('sales_channel').annotate(
            count=Count('id'),
            total_amount=Sum('actual_amount'),
            avg_amount=Avg('actual_amount')
        ).order_by('-total_amount')
        
        # 支付方式统计
        payment_stats = SalesRecord.objects.values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('actual_amount')
        ).order_by('-total_amount')
        
        # 热销商品
        hot_products = SalesItem.objects.select_related('product').values(
            'product__name', 'product__code'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum('subtotal')
        ).order_by('-total_quantity')[:10]

        gross_profit = SalesItem.objects.aggregate(
            total=Sum(gross_profit_expr)
        )['total'] or Decimal(0)

        gross_margin = Decimal(0)
        total_sales_amount = SalesRecord.objects.aggregate(
            total=Sum('actual_amount')
        )['total'] or Decimal(0)
        if total_sales_amount > 0:
            gross_margin = (gross_profit / total_sales_amount) * 100
        
        return Response({
            'today_sales': float(today_sales),
            'yesterday_sales': float(yesterday_sales),
            'month_sales': float(month_sales),
            'total_orders': total_orders,
            'avg_order_amount': float(avg_order_amount),
            'gross_profit': float(gross_profit),
            'gross_margin': float(gross_margin),
            'channel_stats': list(channel_stats),
            'payment_stats': list(payment_stats),
            'hot_products': list(hot_products)
        })
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """获取销售明细"""
        sales_record = self.get_object()
        items = sales_record.items.all().select_related('product')
        serializer = SalesItemSerializer(items, many=True)
        return Response(serializer.data)