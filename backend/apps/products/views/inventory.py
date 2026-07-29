"""
商品库存视图
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, F
from apps.products.models import ProductInventory
from apps.operations.models import OperationLog
from ..serializers import ProductInventorySerializer
from ..permissions import InventoryPermission


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductInventoryViewSet(viewsets.ModelViewSet):
    """商品库存视图集"""
    queryset = ProductInventory.objects.all()
    serializer_class = ProductInventorySerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'warehouse']
    ordering_fields = ['update_time', 'current_stock', 'available_stock']
    ordering = ['-update_time']
    
    def get_queryset(self):
        """根据查询参数过滤库存"""
        queryset = super().get_queryset().select_related('product', 'warehouse')
        
        product_name = self.request.query_params.get('product_name')
        if product_name:
            queryset = queryset.filter(product__name__icontains=product_name)
        
        warehouse_name = self.request.query_params.get('warehouse_name')
        if warehouse_name:
            queryset = queryset.filter(warehouse__name__icontains=warehouse_name)
        
        stock_status = self.request.query_params.get('stock_status')
        if stock_status:
            if stock_status == 'low':
                queryset = queryset.filter(available_stock__lt=F('product__min_stock'))
            elif stock_status == 'normal':
                queryset = queryset.filter(
                    available_stock__gte=F('product__min_stock'),
                    available_stock__lte=F('product__max_stock')
                )
            elif stock_status == 'overstock':
                queryset = queryset.filter(available_stock__gt=F('product__max_stock'))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取库存汇总统计"""
        queryset = ProductInventory.objects.select_related('product', 'warehouse')

        total_value = queryset.aggregate(
            total=Sum(F('current_stock') * F('product__purchase_price'))
        )['total'] or 0

        warehouse_stats = queryset.values(
            'warehouse__name'
        ).annotate(
            total_products=Count('product', distinct=True),
            total_stock=Sum('current_stock'),
            total_value=Sum(F('current_stock') * F('product__purchase_price'))
        ).order_by('warehouse__name')

        product_stats = queryset.values(
            'product__name', 'product__code'
        ).annotate(
            total_stock=Sum('current_stock'),
            total_value=Sum(F('current_stock') * F('product__purchase_price')),
            warehouse_count=Count('warehouse', distinct=True)
        ).order_by('product__name')

        low_stock_warnings = queryset.filter(available_stock__lt=F('product__min_stock')).count()
        overstock_warnings = queryset.filter(
            product__max_stock__isnull=False,
            available_stock__gt=F('product__max_stock')
        ).count()
        
        return Response({
            'total_value': total_value,
            'total_products': queryset.values('product').distinct().count(),
            'total_inventory_records': queryset.count(),
            'total_warehouses': queryset.values('warehouse').distinct().count(),
            'low_stock_warnings': low_stock_warnings,
            'overstock_warnings': overstock_warnings,
            'warehouse_stats': list(warehouse_stats),
            'product_stats': list(product_stats)
        })
    
    @action(detail=False, methods=['get'])
    def stock_alerts(self, request):
        """获取库存预警列表"""
        low_stock_products = []
        overstock_products = []
        
        inventories = ProductInventory.objects.select_related('product', 'warehouse').all()
        
        for inventory in inventories:
            if inventory.is_low_stock():
                low_stock_products.append({
                    'product_id': inventory.product.id,
                    'product_name': inventory.product.name,
                    'warehouse_name': inventory.warehouse.name,
                    'current_stock': inventory.current_stock,
                    'min_stock': inventory.product.min_stock,
                    'warning_level': 'low',
                    'warning_message': f'库存不足: {inventory.current_stock} < {inventory.product.min_stock}'
                })
            
            if inventory.is_overstock():
                overstock_products.append({
                    'product_id': inventory.product.id,
                    'product_name': inventory.product.name,
                    'warehouse_name': inventory.warehouse.name,
                    'current_stock': inventory.current_stock,
                    'max_stock': inventory.product.max_stock,
                    'warning_level': 'overstock',
                    'warning_message': f'库存超限: {inventory.current_stock} > {inventory.product.max_stock}'
                })
        
        return Response({
            'low_stock_alerts': low_stock_products,
            'overstock_alerts': overstock_products
        })
    
    def perform_create(self, serializer):
        """创建库存记录时记录日志"""
        inventory = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.CREATE,
            model_name='ProductInventory',
            object_id=str(inventory.id),
            object_repr=str(inventory),
            action_detail='创建库存记录',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        """更新库存时记录日志"""
        new_instance = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='ProductInventory',
            object_id=str(new_instance.id),
            object_repr=str(new_instance),
            action_detail='更新库存记录',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        """删除库存记录时记录日志"""
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='ProductInventory',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除库存记录',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        instance.delete()