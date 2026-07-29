"""
销售分析视图
"""
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Avg, F, Q
from django.db import transaction
from datetime import datetime, timedelta
from decimal import Decimal
import json
from apps.operations.models import SalesAnalysis, SalesRecord, SalesItem, OperationLog
from ..serializers import SalesAnalysisSerializer, SalesQuerySerializer
from ..permissions import SalesAnalysisPermission, CanGenerateReports
from apps.products.models import Product, ProductInventory


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SalesAnalysisViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """销售分析视图集"""
    queryset = SalesAnalysis.objects.all()
    serializer_class = SalesAnalysisSerializer
    permission_classes = [IsAuthenticated, SalesAnalysisPermission]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """根据查询参数过滤分析数据"""
        queryset = super().get_queryset()
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(analysis_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(analysis_date__lte=end_date)
        
        return queryset
    
    def perform_update(self, serializer):
        """更新分析数据时记录日志"""
        new_instance = serializer.save()
        
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='SalesAnalysis',
            object_id=str(new_instance.id),
            object_repr=str(new_instance),
            action_detail='更新销售分析数据',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
    
    def perform_destroy(self, instance):
        """删除分析数据时记录日志"""
        OperationLog.objects.create(
            user=self.request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='SalesAnalysis',
            object_id=str(instance.id),
            object_repr=str(instance),
            action_detail='删除销售分析数据',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        instance.delete()
    
    @action(detail=False, methods=['post'])
    def generate_analysis(self, request):
        """生成销售分析"""
        data = request.data
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        force_regenerate = data.get('force_regenerate', False)
        
        if not start_date or not end_date:
            return Response(
                {'error': '请提供开始日期和结束日期'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': '日期格式不正确，请使用 YYYY-MM-DD 格式'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # 检查是否已存在分析数据
                existing_analysis = SalesAnalysis.objects.filter(
                    analysis_date__gte=start_date_obj,
                    analysis_date__lte=end_date_obj
                )
                
                if existing_analysis.exists() and not force_regenerate:
                    return Response({
                        'message': f'在 {start_date} 到 {end_date} 期间已存在 {existing_analysis.count()} 条分析数据',
                        'existing_data': existing_analysis.count(),
                        'force_regenerate': False
                    })
                
                if force_regenerate and existing_analysis.exists():
                    existing_analysis.delete()
                
                # 生成每日分析数据
                current_date = start_date_obj
                generated_count = 0
                
                while current_date <= end_date_obj:
                    # 获取当天的销售数据
                    daily_sales = SalesRecord.objects.filter(
                        sales_time__date=current_date
                    )
                    
                    daily_items = SalesItem.objects.filter(
                        sales_record__sales_time__date=current_date
                    )
                    
                    # 计算统计数据
                    total_sales = daily_sales.aggregate(
                        total=Sum('actual_amount')
                    )['total'] or Decimal(0)
                    
                    total_orders = daily_sales.count()
                    total_products = daily_items.aggregate(
                        total=Sum('quantity')
                    )['total'] or 0
                    
                    # 计算平均订单金额
                    avg_order_amount = Decimal(0)
                    if total_orders > 0:
                        avg_order_amount = total_sales / total_orders
                    
                    # 查找热销商品
                    best_selling_product_data = daily_items.values(
                        'product__name'
                    ).annotate(
                        total_quantity=Sum('quantity')
                    ).order_by('-total_quantity').first()
                    
                    best_selling_product = ''
                    best_selling_count = 0
                    
                    if best_selling_product_data:
                        best_selling_product = best_selling_product_data['product__name']
                        best_selling_count = best_selling_product_data['total_quantity']
                    
                    # 创建或更新分析记录
                    analysis, created = SalesAnalysis.objects.get_or_create(
                        analysis_date=current_date,
                        defaults={
                            'total_sales': total_sales,
                            'total_orders': total_orders,
                            'total_products': total_products,
                            'avg_order_amount': avg_order_amount,
                            'best_selling_product': best_selling_product,
                            'best_selling_count': best_selling_count
                        }
                    )
                    
                    if not created:
                        # 更新现有记录
                        analysis.total_sales = total_sales
                        analysis.total_orders = total_orders
                        analysis.total_products = total_products
                        analysis.avg_order_amount = avg_order_amount
                        analysis.best_selling_product = best_selling_product
                        analysis.best_selling_count = best_selling_count
                        analysis.save()
                    
                    generated_count += 1
                    current_date += timedelta(days=1)
                
                # 记录操作日志
                OperationLog.objects.create(
                    user=request.user,
                    action_type=OperationLog.ActionType.CREATE,
                    model_name='SalesAnalysis',
                    object_id='',
                    object_repr=f'生成销售分析 {start_date} 到 {end_date}',
                    action_detail=f'生成销售分析数据，共 {generated_count} 天',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return Response({
                    'message': f'成功生成 {generated_count} 天的销售分析数据',
                    'generated_count': generated_count,
                    'start_date': start_date,
                    'end_date': end_date
                })
                
        except Exception as e:
            return Response(
                {'error': f'生成分析数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[CanGenerateReports])
    def generate_report(self, request):
        """生成销售报告"""
        serializer = SalesQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        start_date = data['start_date']
        end_date = data['end_date']
        sales_channel = data.get('sales_channel')
        payment_method = data.get('payment_method')
        group_by = data.get('group_by', 'day')
        
        # 基本销售数据查询
        sales_queryset = SalesRecord.objects.filter(
            sales_time__date__gte=start_date,
            sales_time__date__lte=end_date
        )
        
        if sales_channel:
            sales_queryset = sales_queryset.filter(sales_channel=sales_channel)
        
        if payment_method:
            sales_queryset = sales_queryset.filter(payment_method=payment_method)
        
        # 计算总体统计
        total_stats = sales_queryset.aggregate(
            total_sales=Sum('actual_amount'),
            total_orders=Count('id'),
            avg_order_amount=Avg('actual_amount'),
            total_discount=Sum('discount_amount')
        )
        
        # 按销售渠道统计
        channel_stats = sales_queryset.values('sales_channel').annotate(
            sales_amount=Sum('actual_amount'),
            order_count=Count('id'),
            avg_amount=Avg('actual_amount')
        ).order_by('-sales_amount')
        
        # 按支付方式统计
        payment_stats = sales_queryset.values('payment_method').annotate(
            sales_amount=Sum('actual_amount'),
            order_count=Count('id')
        ).order_by('-sales_amount')
        
        # 按日期分组统计
        if group_by == 'day':
            date_stats = sales_queryset.values('sales_time__date').annotate(
                daily_sales=Sum('actual_amount'),
                daily_orders=Count('id'),
                daily_avg=Avg('actual_amount')
            ).order_by('sales_time__date')
        elif group_by == 'week':
            # 按周统计
            from django.db import connection
            date_stats = []
        elif group_by == 'month':
            # 按月统计
            from django.db.models.functions import TruncMonth
            date_stats = sales_queryset.annotate(
                month=TruncMonth('sales_time')
            ).values('month').annotate(
                monthly_sales=Sum('actual_amount'),
                monthly_orders=Count('id'),
                monthly_avg=Avg('actual_amount')
            ).order_by('month')
        elif group_by == 'year':
            # 按年统计
            from django.db.models.functions import ExtractYear
            date_stats = sales_queryset.annotate(
                year=ExtractYear('sales_time')
            ).values('year').annotate(
                yearly_sales=Sum('actual_amount'),
                yearly_orders=Count('id'),
                yearly_avg=Avg('actual_amount')
            ).order_by('year')
        
        # 商品销售排名
        product_stats = SalesItem.objects.filter(
            sales_record__sales_time__date__gte=start_date,
            sales_record__sales_time__date__lte=end_date
        ).select_related('product').values(
            'product__name', 'product__code'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum('subtotal'),
            sale_count=Count('sales_record')
        ).order_by('-total_amount')[:20]
        
        # 时间趋势分析
        trend_data = []
        current = start_date
        while current <= end_date:
            day_sales = sales_queryset.filter(
                sales_time__date=current
            ).aggregate(
                amount=Sum('actual_amount')
            )['amount'] or Decimal(0)
            
            trend_data.append({
                'date': current.strftime('%Y-%m-%d'),
                'sales': float(day_sales)
            })
            
            current += timedelta(days=1)
        
        # 客户分析
        customer_stats = sales_queryset.exclude(
            Q(customer_name__isnull=True) | Q(customer_name='')
        ).values('customer_name', 'customer_phone').annotate(
            total_orders=Count('id'),
            total_amount=Sum('actual_amount'),
            avg_amount=Avg('actual_amount')
        ).order_by('-total_amount')[:10]
        
        # 收银员绩效
        cashier_stats = sales_queryset.values(
            'cashier__username', 'cashier__id'
        ).annotate(
            total_orders=Count('id'),
            total_amount=Sum('actual_amount'),
            avg_amount=Avg('actual_amount')
        ).filter(cashier__isnull=False).order_by('-total_amount')
        
        return Response({
            'report_period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': (end_date - start_date).days + 1
            },
            'filters': {
                'sales_channel': sales_channel,
                'payment_method': payment_method,
                'group_by': group_by
            },
            'summary': {
                'total_sales': float(total_stats['total_sales'] or Decimal(0)),
                'total_orders': total_stats['total_orders'] or 0,
                'avg_order_amount': float(total_stats['avg_order_amount'] or Decimal(0)),
                'total_discount': float(total_stats['total_discount'] or Decimal(0))
            },
            'channel_distribution': list(channel_stats),
            'payment_distribution': list(payment_stats),
            'time_distribution': list(date_stats),
            'top_products': list(product_stats),
            'sales_trend': trend_data,
            'top_customers': list(customer_stats),
            'cashier_performance': list(cashier_stats)
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取销售分析统计"""
        # 最近7天销售趋势
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=6)
        
        recent_sales = []
        current_date = seven_days_ago
        while current_date <= today:
            day_total = SalesRecord.objects.filter(
                sales_time__date=current_date
            ).aggregate(
                total=Sum('actual_amount')
            )['total'] or Decimal(0)
            
            recent_sales.append({
                'date': current_date.strftime('%m-%d'),
                'sales': float(day_total)
            })
            
            current_date += timedelta(days=1)
        
        # 月度销售额对比
        current_month_start = today.replace(day=1)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        last_month_end = current_month_start - timedelta(days=1)
        
        current_month_sales = SalesRecord.objects.filter(
            sales_time__date__gte=current_month_start
        ).aggregate(
            total=Sum('actual_amount')
        )['total'] or Decimal(0)
        
        last_month_sales = SalesRecord.objects.filter(
            sales_time__date__gte=last_month_start,
            sales_time__date__lte=last_month_end
        ).aggregate(
            total=Sum('actual_amount')
        )['total'] or Decimal(0)
        
        # 月增长率
        month_growth = 0
        if last_month_sales > 0:
            month_growth = ((current_month_sales - last_month_sales) / last_month_sales) * 100
        
        # 年度销售额
        year_start = today.replace(month=1, day=1)
        year_sales = SalesRecord.objects.filter(
            sales_time__date__gte=year_start
        ).aggregate(
            total=Sum('actual_amount')
        )['total'] or Decimal(0)
        
        # 商品类别销售分布
        category_stats = SalesItem.objects.filter(
            sales_record__sales_time__date__gte=seven_days_ago
        ).select_related('product__category').values(
            'product__category__name'
        ).annotate(
            total_sales=Sum('subtotal'),
            total_quantity=Sum('quantity')
        ).filter(product__category__isnull=False).order_by('-total_sales')[:10]
        
        # 热销商品Top 10
        hot_products = SalesItem.objects.filter(
            sales_record__sales_time__date__gte=seven_days_ago
        ).select_related('product').values(
            'product__name', 'product__code'
        ).annotate(
            total_sales=Sum('subtotal'),
            total_quantity=Sum('quantity')
        ).order_by('-total_sales')[:10]
        
        # 销售渠道分布
        channel_distribution = SalesRecord.objects.filter(
            sales_time__date__gte=seven_days_ago
        ).values('sales_channel').annotate(
            total_sales=Sum('actual_amount'),
            order_count=Count('id')
        ).order_by('-total_sales')
        
        return Response({
            'recent_sales_trend': recent_sales,
            'monthly_comparison': {
                'current_month': float(current_month_sales),
                'last_month': float(last_month_sales),
                'growth_rate': float(month_growth)
            },
            'year_sales': float(year_sales),
            'category_distribution': list(category_stats),
            'hot_products': list(hot_products),
            'channel_distribution': list(channel_distribution)
        })
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """销售分析概览"""
        # 今日销售
        today = datetime.now().date()
        today_sales = SalesRecord.objects.filter(
            sales_time__date=today
        ).aggregate(
            total=Sum('actual_amount'),
            count=Count('id'),
            avg=Avg('actual_amount')
        )
        
        # 昨日销售
        yesterday = today - timedelta(days=1)
        yesterday_sales = SalesRecord.objects.filter(
            sales_time__date=yesterday
        ).aggregate(
            total=Sum('actual_amount'),
            count=Count('id'),
            avg=Avg('actual_amount')
        )
        
        # 本周销售
        week_start = today - timedelta(days=today.weekday())
        week_sales = SalesRecord.objects.filter(
            sales_time__date__gte=week_start
        ).aggregate(
            total=Sum('actual_amount'),
            count=Count('id'),
            avg=Avg('actual_amount')
        )
        
        # 本月销售
        month_start = today.replace(day=1)
        month_sales = SalesRecord.objects.filter(
            sales_time__date__gte=month_start
        ).aggregate(
            total=Sum('actual_amount'),
            count=Count('id'),
            avg=Avg('actual_amount')
        )
        
        # 销售目标完成率
        target_amount = Decimal(100000)  # 示例目标
        month_completion = Decimal(0)
        if month_sales['total']:
            month_completion = (month_sales['total'] / target_amount) * 100
        
        # 活跃用户数
        recent_customers = SalesRecord.objects.filter(
            sales_time__date__gte=week_start
        ).values('customer_phone').distinct().count()
        
        return Response({
            'today': {
                'sales': float(today_sales['total'] or Decimal(0)),
                'orders': today_sales['count'] or 0,
                'avg_order': float(today_sales['avg'] or Decimal(0))
            },
            'yesterday': {
                'sales': float(yesterday_sales['total'] or Decimal(0)),
                'orders': yesterday_sales['count'] or 0,
                'avg_order': float(yesterday_sales['avg'] or Decimal(0))
            },
            'this_week': {
                'sales': float(week_sales['total'] or Decimal(0)),
                'orders': week_sales['count'] or 0,
                'avg_order': float(week_sales['avg'] or Decimal(0))
            },
            'this_month': {
                'sales': float(month_sales['total'] or Decimal(0)),
                'orders': month_sales['count'] or 0,
                'avg_order': float(month_sales['avg'] or Decimal(0)),
                'target_completion': float(month_completion)
            },
            'recent_customers': recent_customers
        })