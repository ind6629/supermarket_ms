"""
用户管理URL配置
"""
from django.urls import path
from .views import (
    LoginView, LogoutView, RefreshTokenView, UserProfileView,
    ChangePasswordView, UserListView, UserDetailView,
    ResetUserPasswordView, ActivateUserView, DeactivateUserView,
    RegisterView, ReviewUserRegistrationView
)

urlpatterns = [
    # 认证相关
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    
    # 个人资料相关
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # 用户管理（管理员权限）
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/reset-password/', ResetUserPasswordView.as_view(), name='reset-password'),
    path('<int:pk>/activate/', ActivateUserView.as_view(), name='activate-user'),
    path('<int:pk>/deactivate/', DeactivateUserView.as_view(), name='deactivate-user'),
    path('<int:pk>/review/', ReviewUserRegistrationView.as_view(), name='review-user-registration'),
]
