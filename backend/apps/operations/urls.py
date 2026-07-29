"""
运营管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OperationLogViewSet, InventoryTransactionViewSet,
    SalesRecordViewSet, CashImportRecordViewSet, SalesAnalysisViewSet
)


# 创建路由器
router = DefaultRouter()
router.register(r'operation-logs', OperationLogViewSet, basename='operation-log')
router.register(r'inventory-transactions', InventoryTransactionViewSet, basename='inventory-transaction')
router.register(r'sales-records', SalesRecordViewSet, basename='sales-record')
router.register(r'cash-imports', CashImportRecordViewSet, basename='cash-import')
router.register(r'sales-analyses', SalesAnalysisViewSet, basename='sales-analysis')

urlpatterns = [
    # 额外的API端点
    path('inventory-transactions/in-out/', 
         InventoryTransactionViewSet.as_view({'post': 'inventory_in_out'}), 
         name='inventory-in-out'),
    path('inventory-transactions/summary/', 
         InventoryTransactionViewSet.as_view({'get': 'inventory_summary'}), 
         name='inventory-summary'),
    
    path('sales-records/create-with-items/', 
         SalesRecordViewSet.as_view({'post': 'create_with_items'}), 
         name='sales-create-with-items'),
    path('sales-records/search/', 
         SalesRecordViewSet.as_view({'post': 'search_sales'}), 
         name='sales-search'),
    path('sales-records/statistics/', 
         SalesRecordViewSet.as_view({'get': 'sales_statistics'}), 
         name='sales-statistics'),
    
    path('operation-logs/recent-activities/', 
         OperationLogViewSet.as_view({'get': 'recent_activities'}), 
         name='recent-activities'),
    path('operation-logs/statistics/', 
         OperationLogViewSet.as_view({'get': 'statistics'}), 
         name='operation-logs-statistics'),
    path('operation-logs/search/', 
         OperationLogViewSet.as_view({'post': 'search'}), 
         name='operation-logs-search'),
    
    path('cash-imports/upload/', 
         CashImportRecordViewSet.as_view({'post': 'upload_cash_data'}), 
         name='cash-import-upload'),
    
    path('sales-analyses/generate/', 
         SalesAnalysisViewSet.as_view({'post': 'generate_analysis'}), 
         name='generate-sales-analysis'),
    path('sales-analyses/overview/', 
         SalesAnalysisViewSet.as_view({'get': 'overview'}), 
         name='sales-analysis-overview'),
    path('sales-analyses/statistics/', 
         SalesAnalysisViewSet.as_view({'get': 'statistics'}), 
         name='sales-analysis-statistics'),
    path('sales-analyses/report/', 
         SalesAnalysisViewSet.as_view({'get': 'generate_report'}), 
         name='sales-analysis-report'),

    # 包含路由器的URL
    path('', include(router.urls)),
]