"""
商品管理序列化器
"""
from django.db.models import Sum
from rest_framework import serializers
from .models import Category, Supplier, Warehouse, Product, ProductInventory
from django.utils import timezone


class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.IntegerField(source='children.count', read_only=True)
    products_count = serializers.IntegerField(source='products.count', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'code', 'name', 'parent', 'parent_name', 'level', 
            'sort_order', 'status', 'remark', 'children_count', 'products_count',
            'create_time', 'update_time'
        ]
        read_only_fields = ['id', 'level', 'create_time', 'update_time']
    
    def validate_parent(self, value):
        """验证父分类"""
        if value and value == self.instance:
            raise serializers.ValidationError("不能选择自己作为父分类")
        return value


class CategoryTreeSerializer(serializers.ModelSerializer):
    """商品分类树形序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'level', 'sort_order', 'status', 'children']
    
    def get_children(self, obj):
        """获取子分类"""
        children = obj.children.filter(status=1).order_by('sort_order', 'code')
        return CategoryTreeSerializer(children, many=True).data


class SupplierSerializer(serializers.ModelSerializer):
    """供货商序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    products_count = serializers.IntegerField(source='products.count', read_only=True)
    stock_ins_count = serializers.IntegerField(source='purchase_transactions.count', read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'code', 'name', 'contact_person', 'phone', 'address', 
            'email', 'credit_rating', 'tax_number', 'bank_account', 'bank_name',
            'status', 'status_display', 'remark', 'products_count', 
            'stock_ins_count', 'create_time', 'update_time'
        ]
        read_only_fields = ['id', 'create_time', 'update_time']


class WarehouseSerializer(serializers.ModelSerializer):
    """仓库序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    inventory_count = serializers.IntegerField(source='inventories.count', read_only=True)
    capacity_used_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'code', 'name', 'address', 'manager', 'manager_name',
            'capacity', 'contact_phone', 'status', 'status_display',
            'remark', 'inventory_count', 'capacity_used_percentage',
            'create_time', 'update_time'
        ]
        read_only_fields = ['id', 'create_time', 'update_time']
    
    def get_capacity_used_percentage(self, obj):
        """计算容量使用百分比"""
        if not obj.capacity:
            return None
        
        # 这里可以添加实际库存容量计算逻辑
        return 0


class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    profit_margin = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    expiry_date = serializers.DateField(read_only=True)
    total_stock = serializers.SerializerMethodField()
    low_stock_warning = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'barcode', 'category', 'category_name',
            'unit', 'unit_display', 'specification', 'purchase_price',
            'sale_price', 'min_stock', 'max_stock', 'supplier', 'supplier_name',
            'brand', 'manufacturer', 'production_date', 'expiry_days',
            'expiry_date', 'status', 'status_display', 'remark',
            'profit_margin', 'total_stock', 'low_stock_warning',
            'create_time', 'update_time'
        ]
        read_only_fields = [
            'id', 'profit_margin', 'expiry_date', 'total_stock', 
            'low_stock_warning', 'create_time', 'update_time'
        ]
    
    def get_total_stock(self, obj):
        """获取商品总库存"""
        try:
            return ProductInventory.objects.filter(product=obj).aggregate(
                total=Sum('current_stock')
            )['total'] or 0
        except:
            return 0
    
    def get_low_stock_warning(self, obj):
        """检查是否需要低库存预警"""
        try:
            total_stock = self.get_total_stock(obj)
            return total_stock < obj.min_stock
        except:
            return False
    
    def validate(self, attrs):
        """验证数据"""
        if attrs.get('max_stock') is not None and attrs.get('min_stock', 0) > attrs['max_stock']:
            raise serializers.ValidationError({
                'min_stock': '最低库存不能大于最高库存'
            })
        
        if attrs.get('sale_price', 0) < attrs.get('purchase_price', 0):
            raise serializers.ValidationError({
                'sale_price': '售价不能低于进价'
            })
        
        return attrs


class ProductInventorySerializer(serializers.ModelSerializer):
    """商品库存序列化器"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    product_min_stock = serializers.IntegerField(source='product.min_stock', read_only=True)
    product_max_stock = serializers.IntegerField(source='product.max_stock', read_only=True)
    low_stock = serializers.BooleanField(read_only=True)
    overstock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ProductInventory
        fields = [
            'id', 'product', 'product_name', 'product_code', 'warehouse', 'warehouse_name',
            'current_stock', 'locked_stock', 'available_stock', 'warning_sent',
            'product_min_stock', 'product_max_stock',
            'last_inventory_time', 'low_stock', 'overstock', 'update_time'
        ]
        read_only_fields = [
            'id', 'product_name', 'product_code', 'warehouse_name', 
            'available_stock', 'product_min_stock', 'product_max_stock',
            'low_stock', 'overstock', 'update_time'
        ]
    
    def validate(self, attrs):
        """验证库存数据"""
        if 'current_stock' in attrs and attrs['current_stock'] < 0:
            raise serializers.ValidationError({
                'current_stock': '当前库存不能为负数'
            })
        
        if 'locked_stock' in attrs and attrs['locked_stock'] < 0:
            raise serializers.ValidationError({
                'locked_stock': '锁定库存不能为负数'
            })
        
        if 'current_stock' in attrs and 'locked_stock' in attrs:
            if attrs['locked_stock'] > attrs['current_stock']:
                raise serializers.ValidationError({
                    'locked_stock': '锁定库存不能大于当前库存'
                })
        
        return attrs
    
    def save(self, **kwargs):
        """保存时自动计算可用库存"""
        instance = super().save(**kwargs)
        instance.available_stock = instance.current_stock - instance.locked_stock
        if instance.available_stock < 0:
            instance.available_stock = 0
        instance.save(update_fields=['available_stock'])
        return instance


class ProductBulkUpdateSerializer(serializers.Serializer):
    """商品批量更新序列化器"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text='商品ID列表'
    )
    operation = serializers.ChoiceField(
        choices=['activate', 'deactivate', 'delete'],
        required=True,
        help_text='操作类型：activate(激活)、deactivate(停用)、delete(删除)'
    )
    
    def validate_ids(self, value):
        """验证ID列表"""
        if not value:
            raise serializers.ValidationError('ID列表不能为空')
        return value


class ProductImportSerializer(serializers.Serializer):
    """商品导入序列化器"""
    file = serializers.FileField(
        required=True,
        help_text='商品数据文件 (支持Excel, CSV)'
    )
    import_type = serializers.ChoiceField(
        choices=['create', 'update', 'upsert'],
        default='upsert',
        help_text='导入类型：create(新增)、update(更新)、upsert(新增或更新)'
    )
    
    def validate_file(self, value):
        """验证文件"""
        # 检查文件扩展名
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        file_name = value.name.lower()
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f'不支持的文件格式，请上传 {", ".join(allowed_extensions)} 格式的文件'
            )
        
        # 检查文件大小 (最大10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError('文件大小不能超过10MB')
        
        return value


class ProductExportSerializer(serializers.Serializer):
    """商品导出序列化器"""
    export_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['id', 'code', 'name', 'barcode', 'category', 'unit', 
                'purchase_price', 'sale_price', 'min_stock', 'status'],
        help_text='导出字段列表'
    )
    format = serializers.ChoiceField(
        choices=['excel', 'csv', 'json'],
        default='excel',
        help_text='导出格式'
    )
    filter_status = serializers.ChoiceField(
        choices=Product.Status.choices,
        required=False,
        allow_null=True,
        help_text='按状态筛选'
    )
    filter_category = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='按分类筛选'
    )
    filter_supplier = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='按供货商筛选'
    )


class ProductStockAlertSerializer(serializers.Serializer):
    """库存预警序列化器"""
    product = ProductSerializer(read_only=True)
    current_stock = serializers.IntegerField()
    min_stock = serializers.IntegerField()
    warehouse_name = serializers.CharField()
    warning_level = serializers.CharField(help_text='预警级别：low(低库存)、overstock(超库存)')
    warning_message = serializers.CharField()
    
    class Meta:
        fields = ['product', 'current_stock', 'min_stock', 'warehouse_name', 
                 'warning_level', 'warning_message']


class ProductStatisticsSerializer(serializers.Serializer):
    """商品统计序列化器"""
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_code = serializers.CharField()
    total_stock = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_stock_count = serializers.IntegerField()
    overstock_count = serializers.IntegerField()
    warehouses = serializers.IntegerField()
    
    class Meta:
        fields = ['product_id', 'product_name', 'product_code', 'total_stock', 
                 'total_value', 'low_stock_count', 'overstock_count', 'warehouses']