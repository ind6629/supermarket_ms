"""
商品管理模型
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from apps.common.models import BaseModel, CodeMixin


class Category(CodeMixin, BaseModel):
    """
    商品分类
    """
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父分类',
        help_text='为空表示一级分类'
    )
    level = models.IntegerField('层级', default=1, editable=False)
    sort_order = models.IntegerField('排序', default=0, help_text='数字越小越靠前')
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类管理'
        ordering = ['level', 'sort_order', 'code']
        indexes = [
            models.Index(fields=['parent', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        """保存时自动计算层级"""
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        super().save(*args, **kwargs)
    
    def clean(self):
        """验证数据"""
        if self.parent and self.parent == self:
            raise ValidationError('不能选择自己作为父分类')
        if self.parent and self.parent.level >= 3:
            raise ValidationError('分类层级不能超过3级')


class Supplier(CodeMixin, BaseModel):
    """
    供货商
    """
    contact_person = models.CharField('联系人', max_length=50)
    phone = models.CharField('联系电话', max_length=20)
    address = models.TextField('地址')
    email = models.EmailField('邮箱', blank=True, null=True)
    credit_rating = models.IntegerField('信用等级', default=3)
    tax_number = models.CharField('税号', max_length=50, blank=True, default='')
    bank_account = models.CharField('银行账号', max_length=100, blank=True, default='')
    bank_name = models.CharField('开户行', max_length=100, blank=True, default='')
    
    class Meta:
        verbose_name = '供货商'
        verbose_name_plural = '供货商管理'
        ordering = ['-create_time']


class Warehouse(CodeMixin, BaseModel):
    """
    仓库
    """
    address = models.TextField('仓库地址')
    manager = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_warehouses',
        verbose_name='仓库管理员',
        limit_choices_to={'role__in': [0, 1, 2]}  # 只有管理员角色才能管理仓库
    )
    capacity = models.DecimalField(
        '仓库容量',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='单位：立方米'
    )
    contact_phone = models.CharField('联系电话', max_length=20, blank=True, default='')
    
    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = '仓库管理'
        ordering = ['-create_time']


class Product(CodeMixin, BaseModel):
    """
    商品信息
    """
    class Unit(models.TextChoices):
        """计量单位枚举"""
        PIECE = 'piece', '件'
        BOX = 'box', '箱'
        BAG = 'bag', '袋'
        BOTTLE = 'bottle', '瓶'
        KG = 'kg', '千克'
        G = 'g', '克'
        LITER = 'L', '升'
        ML = 'ml', '毫升'
        METER = 'm', '米'
    
    barcode = models.CharField('条形码', max_length=50, unique=True, db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name='商品分类'
    )
    unit = models.CharField('单位', max_length=20, choices=Unit.choices, default=Unit.PIECE)
    specification = models.CharField('规格', max_length=100, blank=True, default='', help_text='如：500g/袋')
    purchase_price = models.DecimalField(
        '进价',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='单位：元'
    )
    sale_price = models.DecimalField(
        '售价',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='单位：元'
    )
    min_stock = models.IntegerField('最低库存', default=0, help_text='库存预警阈值')
    max_stock = models.IntegerField('最高库存', null=True, blank=True, help_text='最大库存容量')
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='默认供货商'
    )
    brand = models.CharField('品牌', max_length=100, blank=True, default='')
    manufacturer = models.CharField('生产商', max_length=200, blank=True, default='')
    production_date = models.DateField('生产日期', null=True, blank=True)
    expiry_days = models.IntegerField('保质期天数', null=True, blank=True, help_text='从生产日期起计算')
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品管理'
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['barcode']),
            models.Index(fields=['supplier', 'status']),
        ]
    
    def clean(self):
        """验证数据"""
        if self.max_stock is not None and self.min_stock > self.max_stock:
            raise ValidationError('最低库存不能大于最高库存')
        if self.sale_price < self.purchase_price:
            raise ValidationError('售价不能低于进价')
    
    @property
    def expiry_date(self):
        """计算过期日期"""
        if self.production_date and self.expiry_days:
            from datetime import timedelta
            return self.production_date + timedelta(days=self.expiry_days)
        return None
    
    @property
    def profit_margin(self):
        """计算毛利率"""
        if self.purchase_price == 0:
            return 1.0
        return (self.sale_price - self.purchase_price) / self.purchase_price


class ProductInventory(models.Model):
    """
    商品库存（按仓库）
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name='商品'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name='仓库'
    )
    current_stock = models.IntegerField('当前库存', default=0)
    locked_stock = models.IntegerField('锁定库存', default=0, help_text='已被订单锁定但未出库的数量')
    available_stock = models.IntegerField('可用库存', default=0, editable=False)
    warning_sent = models.BooleanField('已发送预警', default=False)
    last_inventory_time = models.DateTimeField('最后盘点时间', null=True, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '商品库存'
        verbose_name_plural = '商品库存管理'
        unique_together = ['product', 'warehouse']
        ordering = ['-update_time']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['available_stock']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.available_stock}"
    
    def save(self, *args, **kwargs):
        """保存时自动计算可用库存"""
        self.available_stock = self.current_stock - self.locked_stock
        if self.available_stock < 0:
            self.available_stock = 0
        super().save(*args, **kwargs)
    
    def is_low_stock(self):
        """检查是否低于最低库存"""
        return self.available_stock < self.product.min_stock
    
    def is_overstock(self):
        """检查是否超过最高库存"""
        if self.product.max_stock is not None:
            return self.current_stock > self.product.max_stock
        return False