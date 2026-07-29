"""
运营管理序列化器
"""
from rest_framework import serializers
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from .models import (
    OperationLog, InventoryTransaction, SalesRecord, 
    SalesItem, CashImportRecord, SalesAnalysis
)
from apps.users.models import User


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = [
            'id', 'user', 'user_name', 'action_type', 'action_type_display',
            'model_name', 'object_id', 'object_repr', 'action_detail',
            'ip_address', 'user_agent', 'create_time'
        ]
        read_only_fields = ['id', 'create_time']


class OperationLogQuerySerializer(serializers.Serializer):
    """操作日志查询序列化器"""
    start_date = serializers.DateField(required=False, help_text='开始日期')
    end_date = serializers.DateField(required=False, help_text='结束日期')
    user_id = serializers.IntegerField(required=False, help_text='用户ID')
    action_type = serializers.CharField(required=False, help_text='操作类型')
    model_name = serializers.CharField(required=False, help_text='模型名称')


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """库存交易记录序列化器"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    supplier_name = serializers.CharField(source='related_supplier.name', read_only=True, allow_null=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'code', 'transaction_type', 'transaction_type_display',
            'status', 'status_display', 'product', 'product_name', 'product_code',
            'warehouse', 'warehouse_name', 'quantity', 'unit_price', 'total_amount',
            'related_supplier', 'supplier_name', 'related_order', 'remark',
            'transaction_time', 'create_time'
        ]
        read_only_fields = ['id', 'code', 'total_amount', 'create_time']
    
    def validate(self, attrs):
        """验证数据"""
        if 'quantity' in attrs and attrs['quantity'] <= 0:
            raise serializers.ValidationError({
                'quantity': '数量必须大于0'
            })
        
        if 'unit_price' in attrs and attrs['unit_price'] <= 0:
            raise serializers.ValidationError({
                'unit_price': '单价必须大于0'
            })
        
        return attrs


class SalesItemSerializer(serializers.ModelSerializer):
    """销售明细序列化器"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    unit_display = serializers.CharField(source='product.get_unit_display', read_only=True)
    
    class Meta:
        model = SalesItem
        fields = [
            'id', 'product', 'product_name', 'product_code', 'quantity',
            'unit_price', 'subtotal', 'unit_display'
        ]
        read_only_fields = ['id', 'subtotal']


class SalesRecordSerializer(serializers.ModelSerializer):
    """销售记录序列化器"""
    sales_channel_display = serializers.CharField(source='get_sales_channel_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    cashier_name = serializers.CharField(source='cashier.username', read_only=True)
    items = SalesItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = SalesRecord
        fields = [
            'id', 'order_number', 'customer_name', 'customer_phone',
            'sales_channel', 'sales_channel_display', 'payment_method', 'payment_method_display',
            'total_amount', 'discount_amount', 'actual_amount', 'cashier', 'cashier_name',
            'remark', 'sales_time', 'items', 'items_count', 'create_time'
        ]
        read_only_fields = ['id', 'create_time']
    
    def validate(self, attrs):
        """验证销售数据"""
        if 'total_amount' in attrs and attrs['total_amount'] <= 0:
            raise serializers.ValidationError({
                'total_amount': '总金额必须大于0'
            })
        
        if 'actual_amount' in attrs and attrs['actual_amount'] <= 0:
            raise serializers.ValidationError({
                'actual_amount': '实收金额必须大于0'
            })
        
        if 'discount_amount' in attrs and attrs['discount_amount'] < 0:
            raise serializers.ValidationError({
                'discount_amount': '优惠金额不能为负数'
            })
        
        return attrs


class CashImportRecordSerializer(serializers.ModelSerializer):
    """收银数据导入记录序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    import_user_name = serializers.CharField(source='import_user.username', read_only=True)
    
    class Meta:
        model = CashImportRecord
        fields = [
            'id', 'code', 'file_name', 'file_size', 'import_type',
            'status', 'status_display', 'total_records', 'success_count',
            'fail_count', 'error_message', 'import_user', 'import_user_name',
            'import_time', 'create_time'
        ]
        read_only_fields = ['id', 'code', 'import_time', 'create_time']


class CashImportSerializer(serializers.Serializer):
    """收银数据导入序列化器"""
    file = serializers.FileField(required=True, help_text='收银数据文件')
    import_type = serializers.ChoiceField(
        choices=['sales', 'inventory'],
        default='sales',
        help_text='导入类型'
    )
    overwrite = serializers.BooleanField(
        default=False,
        help_text='是否覆盖现有数据'
    )


class SalesAnalysisSerializer(serializers.ModelSerializer):
    """销售分析序列化器"""
    
    class Meta:
        model = SalesAnalysis
        fields = [
            'id', 'analysis_date', 'total_sales', 'total_orders',
            'total_products', 'avg_order_amount', 'best_selling_product',
            'best_selling_count', 'analysis_time'
        ]
        read_only_fields = ['id', 'analysis_time']


class SalesQuerySerializer(serializers.Serializer):
    """销售查询序列化器"""
    start_date = serializers.DateField(required=True, help_text='开始日期')
    end_date = serializers.DateField(required=True, help_text='结束日期')
    sales_channel = serializers.CharField(required=False, help_text='销售渠道')
    payment_method = serializers.CharField(required=False, help_text='支付方式')
    group_by = serializers.ChoiceField(
        choices=['day', 'week', 'month', 'year', 'product'],
        default='day',
        help_text='分组方式'
    )


class SalesStatisticsSerializer(serializers.Serializer):
    """销售统计序列化器"""
    date = serializers.DateField(help_text='日期')
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2, help_text='总销售额')
    order_count = serializers.IntegerField(help_text='订单数')
    product_count = serializers.IntegerField(help_text='商品数')
    avg_amount = serializers.DecimalField(max_digits=10, decimal_places=2, help_text='平均金额')


class ProductSalesSerializer(serializers.Serializer):
    """商品销售序列化器"""
    product_id = serializers.IntegerField(help_text='商品ID')
    product_name = serializers.CharField(help_text='商品名称')
    product_code = serializers.CharField(help_text='商品编码')
    total_quantity = serializers.IntegerField(help_text='总销量')
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, help_text='总金额')


class InventoryInOutSerializer(serializers.Serializer):
    """入库出库序列化器"""
    transaction_type = serializers.ChoiceField(
        choices=['purchase_in', 'sale_out', 'adjust_in', 'adjust_out'],
        required=True,
        help_text='交易类型'
    )
    product_id = serializers.IntegerField(required=True, help_text='商品ID')
    warehouse_id = serializers.IntegerField(required=True, help_text='仓库ID')
    related_supplier_id = serializers.IntegerField(required=False, allow_null=True, help_text='供货商ID')
    quantity = serializers.IntegerField(required=True, min_value=1, help_text='数量')
    unit_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True, 
        min_value=0.01,
        help_text='单价'
    )
    related_order = serializers.CharField(required=False, allow_blank=True, help_text='相关订单')
    remark = serializers.CharField(required=False, allow_blank=True, help_text='备注')
    
    def validate(self, attrs):
        """验证数据"""
        from apps.products.models import Product, ProductInventory, Supplier
        
        product_id = attrs.get('product_id')
        warehouse_id = attrs.get('warehouse_id')
        quantity = attrs.get('quantity')
        transaction_type = attrs.get('transaction_type')
        
        try:
            product = Product.objects.get(id=product_id, status=1)
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': '商品不存在或已停用'
            })
        
        try:
            inventory = ProductInventory.objects.get(product_id=product_id, warehouse_id=warehouse_id)
        except ProductInventory.DoesNotExist:
            inventory = None
        
        if transaction_type in ['sale_out', 'adjust_out']:
            if not inventory or inventory.available_stock < quantity:
                raise serializers.ValidationError({
                    'quantity': '库存不足'
                })

        related_supplier_id = attrs.get('related_supplier_id')
        if transaction_type == 'purchase_in' and not related_supplier_id:
            raise serializers.ValidationError({
                'related_supplier_id': '采购入库必须选择供货商'
            })

        if related_supplier_id not in [None, '']:
            try:
                Supplier.objects.get(id=related_supplier_id, status=1)
            except Supplier.DoesNotExist:
                raise serializers.ValidationError({
                    'related_supplier_id': '供货商不存在或已停用'
                })
        
        return attrs