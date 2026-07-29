"""
供货商视图
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from apps.products.models import Supplier
from apps.operations.models import OperationLog
from ..serializers import SupplierSerializer
from ..permissions import SupplierPermission


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SupplierViewSet(viewsets.ModelViewSet):
    """供货商视图集"""
    queryset = Supplier.objects.exclude(status=Supplier.Status.DELETED)
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, SupplierPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['code', 'name', 'contact_person', 'phone', 'address', 'email']
    ordering_fields = ['code', 'name', 'create_time', 'credit_rating']
    ordering = ['-create_time']
    
    def get_queryset(self):
        """根据查询参数过滤供货商"""
        queryset = super().get_queryset()
        
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            try:
                queryset = queryset.filter(credit_rating__gte=int(min_rating))
            except ValueError:
                pass
        
        has_products = self.request.query_params.get('has_products')
        if has_products == 'true':
            queryset = queryset.annotate(product_count=Count('products')).filter(product_count__gt=0)
        elif has_products == 'false':
            queryset = queryset.annotate(product_count=Count('products')).filter(product_count=0)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取供货商统计信息"""
        total_suppliers = Supplier.objects.filter(status=1).count()
        
        active_suppliers = Supplier.objects.filter(status=1).annotate(
            product_count=Count('products')
        ).count()
        
        average_rating = Supplier.objects.filter(status=1).aggregate(
            avg_rating=Avg('credit_rating')
        )['avg_rating'] or 0
        
        rating_stats = Supplier.objects.filter(status=1).values(
            'credit_rating'
        ).annotate(
            count=Count('id')
        ).order_by('credit_rating')
        
        return Response({
            'total_suppliers': total_suppliers,
            'active_suppliers': active_suppliers,
            'average_rating': float(average_rating),
            'rating_stats': list(rating_stats)
        })
    
    def perform_create(self, serializer):
        """创建供货商时记录日志"""
        supplier = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.CREATE,
            model_name='Supplier',
            object_id=str(supplier.id),
            object_repr=str(supplier),
            action_detail='创建供货商',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        """更新供货商时记录日志"""
        new_instance = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='Supplier',
            object_id=str(new_instance.id),
            object_repr=str(new_instance),
            action_detail='更新供货商信息',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        """删除供货商时软删除并记录日志"""
        instance.soft_delete(self.request.user)
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='Supplier',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除供货商',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )