"""
用户视图模块
"""
from .auth import (
    LoginView, LogoutView, RefreshTokenView, UserProfileView,
    ChangePasswordView, RegisterView
)
from .user import (
    UserListView, UserDetailView, ResetUserPasswordView,
    ActivateUserView, DeactivateUserView, ReviewUserRegistrationView
)

__all__ = [
    'LoginView',
    'LogoutView',
    'RefreshTokenView',
    'UserProfileView',
    'ChangePasswordView',
    'RegisterView',
    'UserListView',
    'UserDetailView',
    'ResetUserPasswordView',
    'ActivateUserView',
    'DeactivateUserView',
    'ReviewUserRegistrationView',
]
