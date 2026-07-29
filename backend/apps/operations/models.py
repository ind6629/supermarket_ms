"""
运营管理模型
"""
from decimal import Decimal
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel, CodeMixin


class OperationLog(BaseModel):
    """操作日志"""
    class ActionType(models.TextChoices):
        CREATE = 'create', '创建'
        UPDATE = 'update', '更新'
        DELETE = 'delete', '删除'
        IMPORT = 'import', '导入'
        EXPORT = 'export', '导出'
        LOGIN = 'login', '登录'
        LOGOUT = 'logout', '登出'
        INVENTORY_IN = 'inventory_in', '入库'
        INVENTORY_OUT = 'inventory_out', '出库'
        SALE = 'sale', '销售'
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='operation_logs',
        verbose_name='操作用户'
    )
    action_type = models.CharField('操作类型', max_length=20, choices=ActionType.choices)
    model_name = models.CharField('模型名称', max_length=100)
    object_id = models.CharField('对象ID', max_length=100, blank=True, default='')
    object_repr = models.CharField('对象表示', max_length=200, blank=True, default='')
    action_detail = models.TextField('操作详情', blank=True, default='')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True, default='')
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志管理'
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['user', 'create_time']),
            models.Index(fields=['action_type', 'create_time']),
            models.Index(fields=['model_name', 'create_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.get_action_type_display()} - {self.model_name}"


class InventoryTransaction(BaseModel, CodeMixin):
    """库存交易记录"""
    class TransactionType(models.TextChoices):
        PURCHASE_IN = 'purchase_in', '采购入库'
        PURCHASE_RETURN = 'purchase_return', '采购退货'
        SALE_OUT = 'sale_out', '销售出库'
        SALE_RETURN = 'sale_return', '销售退货'
        ADJUST_IN = 'adjust_in', '调整入库'
        ADJUST_OUT = 'adjust_out', '调整出库'
        TRANSFER = 'transfer', '调拨'
    
    class TransactionStatus(models.TextChoices):
        PENDING = 'pending', '待处理'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'
    
    transaction_type = models.CharField('交易类型', max_length=20, choices=TransactionType.choices)
    status = models.CharField('状态', max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='inventory_transactions',
        verbose_name='商品'
    )
    warehouse = models.ForeignKey(
        'products.Warehouse',
        on_delete=models.CASCADE,
        related_name='inventory_transactions',
        verbose_name='仓库'
    )
    quantity = models.IntegerField('数量', validators=[MinValueValidator(1)])
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    related_supplier = models.ForeignKey(
        'products.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_transactions',
        verbose_name='相关供货商'
    )
    related_order = models.CharField('相关订单', max_length=100, blank=True, default='')
    remark = models.TextField('备注', blank=True, default='')
    transaction_time = models.DateTimeField('交易时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '库存交易记录'
        verbose_name_plural = '库存交易记录管理'
        ordering = ['-transaction_time']
        indexes = [
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['product', 'transaction_time']),
            models.Index(fields=['warehouse', 'transaction_time']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.get_transaction_type_display()} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        """保存时自动计算总金额"""
        if not self.code:
            self.code = f"IT{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        if not self.name:
            product_name = self.product.name if self.product_id else '库存交易'
            self.name = f"{self.get_transaction_type_display()}-{product_name}"
        if not self.total_amount:
            self.total_amount = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)


class SalesRecord(BaseModel, CodeMixin):
    """销售记录"""
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', '现金'
        WECHAT = 'wechat', '微信支付'
        ALIPAY = 'alipay', '支付宝'
        CARD = 'card', '银行卡'
        UNIONPAY = 'unionpay', '云闪付'
    
    class SalesChannel(models.TextChoices):
        STORE = 'store', '门店'
        ONLINE = 'online', '线上'
        WHOLESALE = 'wholesale', '批发'
    
    order_number = models.CharField('订单号', max_length=50, unique=True, db_index=True)
    customer_name = models.CharField('客户姓名', max_length=100, blank=True, default='')
    customer_phone = models.CharField('客户电话', max_length=20, blank=True, default='')
    sales_channel = models.CharField('销售渠道', max_length=20, choices=SalesChannel.choices, default=SalesChannel.STORE)
    payment_method = models.CharField('支付方式', max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField('优惠金额', max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    actual_amount = models.DecimalField('实收金额', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    cashier = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales_records',
        verbose_name='收银员'
    )
    remark = models.TextField('备注', blank=True, default='')
    sales_time = models.DateTimeField('销售时间')
    
    class Meta:
        verbose_name = '销售记录'
        verbose_name_plural = '销售记录管理'
        ordering = ['-sales_time']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['sales_time']),
            models.Index(fields=['customer_name']),
            models.Index(fields=['cashier']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - ¥{self.actual_amount}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.order_number
        if not self.name:
            self.name = self.order_number
        super().save(*args, **kwargs)


class SalesItem(BaseModel):
    """销售明细"""
    sales_record = models.ForeignKey(
        SalesRecord,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='销售记录'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='sales_items',
        verbose_name='商品'
    )
    quantity = models.IntegerField('数量', validators=[MinValueValidator(1)])
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    subtotal = models.DecimalField('小计', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        verbose_name = '销售明细'
        verbose_name_plural = '销售明细管理'
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['sales_record', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """保存时自动计算小计"""
        if not self.subtotal:
            self.subtotal = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)


class CashImportRecord(BaseModel, CodeMixin):
    """收银数据导入记录"""
    class ImportStatus(models.TextChoices):
        PENDING = 'pending', '待处理'
        PROCESSING = 'processing', '处理中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    file_name = models.CharField('文件名', max_length=200)
    file_size = models.IntegerField('文件大小(B)')
    import_type = models.CharField('导入类型', max_length=20, default='sales')
    status = models.CharField('状态', max_length=20, choices=ImportStatus.choices, default=ImportStatus.PENDING)
    total_records = models.IntegerField('总记录数', default=0)
    success_count = models.IntegerField('成功数', default=0)
    fail_count = models.IntegerField('失败数', default=0)
    error_message = models.TextField('错误信息', blank=True, default='')
    import_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='cash_imports',
        verbose_name='导入用户'
    )
    import_time = models.DateTimeField('导入时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '收银数据导入记录'
        verbose_name_plural = '收银数据导入记录管理'
        ordering = ['-import_time']
    
    def __str__(self):
        return f"{self.file_name} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"IMP{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        if not self.name:
            self.name = self.file_name or self.code
        super().save(*args, **kwargs)


class SalesAnalysis(BaseModel):
    """销售分析数据"""
    analysis_date = models.DateField('分析日期', unique=True, db_index=True)
    total_sales = models.DecimalField('总销售额', max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField('总订单数', default=0)
    total_products = models.IntegerField('总商品数', default=0)
    avg_order_amount = models.DecimalField('平均订单金额', max_digits=10, decimal_places=2, default=0)
    best_selling_product = models.CharField('热销商品', max_length=200, blank=True, default='')
    best_selling_count = models.IntegerField('热销数量', default=0)
    analysis_time = models.DateTimeField('分析时间', auto_now=True)
    
    class Meta:
        verbose_name = '销售分析'
        verbose_name_plural = '销售分析管理'
        ordering = ['-analysis_date']
        indexes = [
            models.Index(fields=['analysis_date']),
        ]
    
    def __str__(self):
        return f"销售分析 - {self.analysis_date}"