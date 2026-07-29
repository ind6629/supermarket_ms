"""
商品视图
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, F
from django.db import transaction
from apps.products.models import Product, Category, ProductInventory
from apps.operations.models import OperationLog
from ..serializers import ProductSerializer, ProductBulkUpdateSerializer
from ..permissions import ProductPermission


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    """商品视图集"""
    queryset = Product.objects.exclude(status=Product.Status.DELETED)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, ProductPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'supplier', 'status']
    search_fields = ['code', 'name', 'barcode', 'brand', 'manufacturer']
    ordering_fields = ['code', 'name', 'sale_price', 'purchase_price', 'create_time']
    ordering = ['-create_time']
    
    def get_queryset(self):
        """根据查询参数过滤商品"""
        queryset = super().get_queryset()
        
        category_id = self.request.query_params.get('category_id')
        if category_id:
            try:
                category = Category.objects.get(id=category_id, status=1)
                category_ids = self._get_all_subcategory_ids(category)
                queryset = queryset.filter(category_id__in=category_ids)
            except Category.DoesNotExist:
                pass
        
        stock_status = self.request.query_params.get('stock_status')
        if stock_status:
            if stock_status == 'low':
                queryset = queryset.annotate(
                    total_stock=Sum('inventories__current_stock')
                ).filter(total_stock__lt=F('min_stock'))
            elif stock_status == 'overstock':
                queryset = queryset.annotate(
                    total_stock=Sum('inventories__current_stock')
                ).filter(total_stock__gt=F('max_stock'))
            elif stock_status == 'normal':
                queryset = queryset.annotate(
                    total_stock=Sum('inventories__current_stock')
                ).filter(total_stock__gte=F('min_stock'), total_stock__lte=F('max_stock'))
        
        return queryset
    
    def _get_all_subcategory_ids(self, category):
        """获取分类及其所有子分类的ID"""
        category_ids = [category.id]
        children = category.children.filter(status=1)
        
        for child in children:
            category_ids.extend(self._get_all_subcategory_ids(child))
        
        return category_ids
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """批量更新商品状态"""
        serializer = ProductBulkUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_ids = serializer.validated_data['ids']
        operation = serializer.validated_data['operation']
        
        try:
            with transaction.atomic():
                products = Product.objects.filter(id__in=product_ids, status__in=[0, 1])
                
                if operation == 'activate':
                    for product in products:
                        product.activate(request.user)
                    message = f'成功激活 {len(products)} 个商品'
                elif operation == 'deactivate':
                    for product in products:
                        product.deactivate(request.user)
                    message = f'成功停用 {len(products)} 个商品'
                elif operation == 'delete':
                    for product in products:
                        product.soft_delete(request.user)
                    message = f'成功删除 {len(products)} 个商品'
                else:
                    return Response(
                        {'error': '不支持的操作类型'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                OperationLog.objects.create(
                    user=request.user,
                    action_type=OperationLog.ActionType.UPDATE,
                    model_name='Product',
                    object_id=','.join(str(id) for id in product_ids),
                    object_repr=f'批量操作 {len(products)} 个商品',
                    action_detail=f'批量{operation}商品',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return Response({'message': message})
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stock_alerts(self, request):
        """获取库存预警列表"""
        low_stock_products = []
        inventories = ProductInventory.objects.select_related('product', 'warehouse').all()
        
        for inventory in inventories:
            if inventory.available_stock < inventory.product.min_stock:
                low_stock_products.append({
                    'product': inventory.product.name,
                    'current_stock': inventory.current_stock,
                    'min_stock': inventory.product.min_stock,
                    'warehouse': inventory.warehouse.name,
                    'warning_level': 'low',
                    'warning_message': f'库存不足: {inventory.current_stock} < {inventory.product.min_stock}'
                })
        
        return Response(low_stock_products)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取商品统计信息"""
        total_products = Product.objects.filter(status=1).count()
        
        category_stats = Category.objects.filter(status=1).annotate(
            product_count=Count('products', filter=Q(products__status=1))
        ).values('id', 'name', 'product_count')
        
        status_stats = Product.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        return Response({
            'total_products': total_products,
            'category_stats': list(category_stats),
            'status_stats': list(status_stats)
        })
    
    def perform_create(self, serializer):
        """创建商品时记录日志"""
        product = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.CREATE,
            model_name='Product',
            object_id=str(product.id),
            object_repr=str(product),
            action_detail='创建商品',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        """更新商品时记录日志"""
        new_instance = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='Product',
            object_id=str(new_instance.id),
            object_repr=str(new_instance),
            action_detail='更新商品信息',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        """删除商品时软删除并记录日志"""
        instance.soft_delete(self.request.user)
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='Product',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除商品',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
