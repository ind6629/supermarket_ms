"""
用户权限类
"""
from rest_framework import permissions
from .models import User


class IsSuperAdmin(permissions.BasePermission):
    """超级管理员权限"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == User.Role.SUPER_ADMIN)


class IsAdmin(permissions.BasePermission):
    """管理员权限"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role in [User.Role.SUPER_ADMIN, User.Role.ADMIN])


class IsInventoryManager(permissions.BasePermission):
    """库存管理员权限"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role in [User.Role.SUPER_ADMIN, User.Role.ADMIN, 
                                        User.Role.INVENTORY_MANAGER])


class IsFinance(permissions.BasePermission):
    """财务人员权限"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role in [User.Role.SUPER_ADMIN, User.Role.ADMIN, 
                                        User.Role.FINANCE])


class IsCashier(permissions.BasePermission):
    """收银员权限"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsOwnerOrAdmin(permissions.BasePermission):
    """用户本人或管理员权限"""
    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.SUPER_ADMIN, User.Role.ADMIN]:
            return True
        
        if hasattr(obj, 'id') and obj.id == request.user.id:
            return True
        
        return False


class IsActiveUser(permissions.BasePermission):
    """活跃用户权限"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.is_active and request.user.status == User.Status.ACTIVE)
