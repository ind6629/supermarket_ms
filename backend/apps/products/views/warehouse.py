"""
仓库视图
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Warehouse
from apps.operations.models import OperationLog
from ..serializers import WarehouseSerializer
from ..permissions import WarehousePermission


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class WarehouseViewSet(viewsets.ModelViewSet):
    """仓库视图集"""
    queryset = Warehouse.objects.exclude(status=Warehouse.Status.DELETED)
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, WarehousePermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['code', 'name', 'address', 'contact_phone']
    ordering_fields = ['code', 'name', 'create_time']
    ordering = ['-create_time']
    
    def get_queryset(self):
        """根据查询参数过滤仓库"""
        queryset = super().get_queryset()
        
        manager_id = self.request.query_params.get('manager_id')
        if manager_id:
            queryset = queryset.filter(manager_id=manager_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """创建仓库时记录日志"""
        warehouse = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.CREATE,
            model_name='Warehouse',
            object_id=str(warehouse.id),
            object_repr=str(warehouse),
            action_detail='创建仓库',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        """更新仓库时记录日志"""
        new_instance = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='Warehouse',
            object_id=str(new_instance.id),
            object_repr=str(new_instance),
            action_detail='更新仓库信息',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        """删除仓库时软删除并记录日志"""
        instance.soft_delete(self.request.user)
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='Warehouse',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除仓库',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )