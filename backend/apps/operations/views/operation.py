"""
操作日志视图
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from apps.operations.models import OperationLog
from ..serializers import OperationLogSerializer, OperationLogQuerySerializer
from ..permissions import OperationLogPermission


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class OperationLogViewSet(viewsets.ModelViewSet):
    """操作日志视图集"""
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated, OperationLogPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action_type', 'model_name', 'user']
    search_fields = ['object_repr', 'action_detail', 'ip_address', 'user__username']
    ordering_fields = ['create_time']
    ordering = ['-create_time']
    
    def get_queryset(self):
        """根据查询参数过滤日志"""
        queryset = super().get_queryset()
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(create_time__date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(create_time__date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取操作日志统计"""
        queryset = self.get_queryset()
        
        # 总操作数
        total_operations = queryset.count()
        
        # 按操作类型统计
        action_stats = queryset.values('action_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按模型统计
        model_stats = queryset.values('model_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按用户统计
        user_stats = queryset.values('user__username').annotate(
            count=Count('id')
        ).filter(user__username__isnull=False).order_by('-count')
        
        # 今日操作数
        from django.utils import timezone
        today = timezone.now().date()
        today_operations = queryset.filter(
            create_time__date=today
        ).count()
        
        return Response({
            'total_operations': total_operations,
            'today_operations': today_operations,
            'action_stats': list(action_stats),
            'model_stats': list(model_stats),
            'user_stats': list(user_stats)
        })
    
    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """获取最近活动"""
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset().select_related('user')[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """高级搜索"""
        serializer = OperationLogQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        queryset = self.get_queryset()
        
        # 应用过滤条件
        data = serializer.validated_data
        
        if data.get('start_date'):
            queryset = queryset.filter(create_time__date__gte=data['start_date'])
        
        if data.get('end_date'):
            queryset = queryset.filter(create_time__date__lte=data['end_date'])
        
        if data.get('user_id'):
            queryset = queryset.filter(user_id=data['user_id'])
        
        if data.get('action_type'):
            queryset = queryset.filter(action_type=data['action_type'])
        
        if data.get('model_name'):
            queryset = queryset.filter(model_name__icontains=data['model_name'])
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)