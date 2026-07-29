"""
商品分类视图
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from apps.products.models import Category
from apps.operations.models import OperationLog
from ..serializers import CategorySerializer, CategoryTreeSerializer
from ..permissions import CategoryPermission


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """商品分类视图集"""
    queryset = Category.objects.filter(status=1)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, CategoryPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'level', 'status']
    search_fields = ['code', 'name']
    ordering_fields = ['level', 'sort_order', 'create_time']
    ordering = ['level', 'sort_order', 'code']
    
    def get_queryset(self):
        """根据查询参数过滤分类"""
        queryset = super().get_queryset()
        
        parent_id = self.request.query_params.get('parent_id')
        if parent_id is not None:
            if parent_id == 'null' or parent_id == '':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取分类树形结构"""
        root_categories = Category.objects.filter(parent__isnull=True, status=1).order_by('sort_order', 'code')
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """移动分类"""
        category = self.get_object()
        new_parent_id = request.data.get('parent_id')
        new_sort_order = request.data.get('sort_order', 0)
        
        try:
            with transaction.atomic():
                if new_parent_id is not None:
                    if new_parent_id == '':
                        category.parent = None
                    else:
                        try:
                            parent = Category.objects.get(id=new_parent_id, status=1)
                            category.parent = parent
                        except Category.DoesNotExist:
                            return Response(
                                {'error': '父分类不存在'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                
                category.sort_order = new_sort_order
                category.save()
                
                OperationLog.objects.create(
                    user=request.user,
                    action_type=OperationLog.ActionType.UPDATE,
                    model_name='Category',
                    object_id=str(category.id),
                    object_repr=str(category),
                    action_detail=f'移动分类',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return Response(CategorySerializer(category).data)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        """创建分类时记录日志"""
        category = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.CREATE,
            model_name='Category',
            object_id=str(category.id),
            object_repr=str(category),
            action_detail='创建商品分类',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_update(self, serializer):
        """更新分类时记录日志"""
        new_instance = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='Category',
            object_id=str(new_instance.id),
            object_repr=str(new_instance),
            action_detail='更新商品分类',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        """删除分类时软删除并记录日志"""
        instance.soft_delete(self.request.user)
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='Category',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除商品分类',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
