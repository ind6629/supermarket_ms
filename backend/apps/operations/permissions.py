"""
运营管理权限类
"""
from rest_framework import permissions
from apps.users.models import User


class OperationLogPermission(permissions.BasePermission):
    """操作日志权限"""
    def has_permission(self, request, view):
        # 所有认证用户都可以查看
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 只有管理员可以修改操作日志
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN
        ]


class InventoryTransactionPermission(permissions.BasePermission):
    """库存交易权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 所有认证用户都可以查看
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 只有管理员、库存管理员、收银员可以创建交易
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.INVENTORY_MANAGER,
            User.Role.CASHIER
        ]


class SalesRecordPermission(permissions.BasePermission):
    """销售记录权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 所有认证用户都可以查看
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 只有管理员、收银员、财务可以创建销售记录
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.CASHIER,
            User.Role.FINANCE
        ]


class SalesAnalysisPermission(permissions.BasePermission):
    """销售分析权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 所有认证用户都可以查看销售分析
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 只有管理员、财务可以修改分析数据
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.FINANCE
        ]


class CashImportPermission(permissions.BasePermission):
    """收银数据导入权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 只有管理员、财务、收银员可以导入收银数据
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.FINANCE,
            User.Role.CASHIER
        ]


class CanExportSalesData(permissions.BasePermission):
    """销售数据导出权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.FINANCE,
            User.Role.CASHIER,
            User.Role.INVENTORY_MANAGER
        ]


class CanGenerateReports(permissions.BasePermission):
    """报表生成权限"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        return user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.ADMIN,
            User.Role.FINANCE,
            User.Role.INVENTORY_MANAGER
        ]