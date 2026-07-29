"""
商品管理权限类
"""
from rest_framework import permissions
from apps.users.models import User


class ProductPermission(permissions.BasePermission):
    """商品管理权限"""
    def has_permission(self, request, view):
        # 所有认证用户都可以查看
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 只有管理员和库存管理员可以修改
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.INVENTORY_MANAGER
        ]


class CategoryPermission(permissions.BasePermission):
    """商品分类权限"""
    def has_permission(self, request, view):
        # 所有认证用户都可以查看
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 只有管理员可以修改分类
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN
        ]


class SupplierPermission(permissions.BasePermission):
    """供货商管理权限"""
    def has_permission(self, request, view):
        # 所有认证用户都可以查看
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 只有管理员和库存管理员可以修改供货商
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.INVENTORY_MANAGER
        ]


class WarehousePermission(permissions.BasePermission):
    """仓库管理权限"""
    def has_permission(self, request, view):
        # 所有认证用户都可以查看
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 只有管理员和库存管理员可以修改仓库
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.INVENTORY_MANAGER
        ]


class InventoryPermission(permissions.BasePermission):
    """库存管理权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 所有认证用户都可以查看库存
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 只有管理员和库存管理员可以修改库存
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.INVENTORY_MANAGER
        ]


class CanImportProduct(permissions.BasePermission):
    """商品导入权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.INVENTORY_MANAGER
        ]


class CanExportProduct(permissions.BasePermission):
    """商品导出权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.INVENTORY_MANAGER,
            User.Role.FINANCE,
            User.Role.CASHIER
        ]