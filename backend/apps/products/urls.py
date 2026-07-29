"""
商品管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SupplierViewSet, WarehouseViewSet,
    ProductViewSet, ProductInventoryViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventories', ProductInventoryViewSet, basename='inventory')

urlpatterns = [
    # 额外的API端点
    path('categories/tree/', CategoryViewSet.as_view({'get': 'tree'}), name='category-tree'),
    path('categories/<int:pk>/move/', CategoryViewSet.as_view({'post': 'move'}), name='category-move'),
    
    # 批量操作
    path('products/bulk-update/', ProductViewSet.as_view({'post': 'bulk_update'}), name='product-bulk-update'),
    path('products/import/', ProductViewSet.as_view({'post': 'import_data'}), name='product-import'),
    path('products/export/', ProductViewSet.as_view({'post': 'export_data'}), name='product-export'),
    path('products/stock-alerts/', ProductViewSet.as_view({'get': 'stock_alerts'}), name='product-stock-alerts'),
    path('products/statistics/', ProductViewSet.as_view({'get': 'statistics'}), name='product-statistics'),
    
    # 库存汇总
    path('inventories/summary/', ProductInventoryViewSet.as_view({'get': 'summary'}), name='inventory-summary'),
    path('inventories/stock-alerts/', ProductInventoryViewSet.as_view({'get': 'stock_alerts'}), name='inventory-stock-alerts'),

    # 包含路由器的URL
    path('', include(router.urls)),
]