"""
超市库存管理系统 - 主URL路由配置
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import JsonResponse

def home_view(request):
    """首页视图"""
    return JsonResponse({
        'message': '超市库存管理系统 API',
        'version': '1.0.0',
        'status': 'running',
        'api_endpoints': {
            '认证接口': '/api/auth/',
            '用户管理': '/api/users/',
            '商品管理': '/api/products/',
            '运营管理': '/api/operations/',
            'API文档': '/api/docs/',
            '管理后台': '/admin/'
        }
    })

urlpatterns = [
    # 首页
    path('', home_view, name='home'),
    
    # Django 管理员后台
    path('admin/', admin.site.urls),
    
    # API 文档
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # 用户认证和管理API
    path('api/auth/', include('apps.users.urls')),
    path('api/users/', include('apps.users.urls')),
    
    # 商品管理API
    path('api/products/', include('apps.products.urls')),
    
    # 运营管理API
    path('api/operations/', include('apps.operations.urls')),
]

# 开发环境下的静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass