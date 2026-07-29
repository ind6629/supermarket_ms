from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


def migrate_operation_log_action_types(apps, schema_editor):
    OperationLog = apps.get_model("operations", "OperationLog")
    action_type_map = {
        "1": "login",
        "2": "logout",
        "3": "create",
        "4": "update",
        "5": "delete",
        "6": "import",
        "7": "export",
        "8": "update",
        "9": "update",
        "99": "update",
    }
    for old_value, new_value in action_type_map.items():
        OperationLog.objects.filter(action_type=old_value).update(action_type=new_value)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("products", "0002_supplier_credit_rating"),
        ("operations", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="operationlog",
                    name="create_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="创建人",
                    ),
                ),
                migrations.AddField(
                    model_name="operationlog",
                    name="remark",
                    field=models.TextField(blank=True, default="", verbose_name="备注"),
                ),
                migrations.AddField(
                    model_name="operationlog",
                    name="status",
                    field=models.IntegerField(
                        choices=[(0, "停用"), (1, "启用"), (2, "已删除")],
                        default=1,
                        verbose_name="状态",
                    ),
                ),
                migrations.AddField(
                    model_name="operationlog",
                    name="update_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="updated_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="更新人",
                    ),
                ),
                migrations.AddField(
                    model_name="operationlog",
                    name="update_time",
                    field=models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterField(
            model_name="operationlog",
            name="action_type",
            field=models.CharField(
                choices=[
                    ("create", "创建"),
                    ("update", "更新"),
                    ("delete", "删除"),
                    ("import", "导入"),
                    ("export", "导出"),
                    ("login", "登录"),
                    ("logout", "登出"),
                    ("inventory_in", "入库"),
                    ("inventory_out", "出库"),
                    ("sale", "销售"),
                ],
                max_length=20,
                verbose_name="操作类型",
            ),
        ),
        migrations.AlterField(
            model_name="operationlog",
            name="object_id",
            field=models.CharField(blank=True, default="", max_length=100, verbose_name="对象ID"),
        ),
        migrations.RunPython(migrate_operation_log_action_types, migrations.RunPython.noop),
        migrations.CreateModel(
            name="InventoryTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("create_time", models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name="创建时间")),
                ("update_time", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("remark", models.TextField(blank=True, default="", verbose_name="备注")),
                ("code", models.CharField(db_index=True, max_length=50, unique=True, verbose_name="编码")),
                ("name", models.CharField(max_length=100, verbose_name="名称")),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[
                            ("purchase_in", "采购入库"),
                            ("purchase_return", "采购退货"),
                            ("sale_out", "销售出库"),
                            ("sale_return", "销售退货"),
                            ("adjust_in", "调整入库"),
                            ("adjust_out", "调整出库"),
                            ("transfer", "调拨"),
                        ],
                        max_length=20,
                        verbose_name="交易类型",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "待处理"), ("completed", "已完成"), ("cancelled", "已取消")],
                        default="pending",
                        max_length=20,
                        verbose_name="状态",
                    ),
                ),
                ("quantity", models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name="数量")),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name="单价")),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name="总金额")),
                ("related_order", models.CharField(blank=True, default="", max_length=100, verbose_name="相关订单")),
                ("transaction_time", models.DateTimeField(auto_now_add=True, verbose_name="交易时间")),
                ("create_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="创建人")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="inventory_transactions", to="products.product", verbose_name="商品")),
                ("related_supplier", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="purchase_transactions", to="products.supplier", verbose_name="相关供货商")),
                ("update_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="更新人")),
                ("warehouse", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="inventory_transactions", to="products.warehouse", verbose_name="仓库")),
            ],
            options={
                "verbose_name": "库存交易记录",
                "verbose_name_plural": "库存交易记录管理",
                "ordering": ["-transaction_time"],
            },
        ),
        migrations.CreateModel(
            name="SalesRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("create_time", models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name="创建时间")),
                ("update_time", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("status", models.IntegerField(choices=[(0, "停用"), (1, "启用"), (2, "已删除")], default=1, verbose_name="状态")),
                ("remark", models.TextField(blank=True, default="", verbose_name="备注")),
                ("code", models.CharField(db_index=True, max_length=50, unique=True, verbose_name="编码")),
                ("name", models.CharField(max_length=100, verbose_name="名称")),
                ("order_number", models.CharField(db_index=True, max_length=50, unique=True, verbose_name="订单号")),
                ("customer_name", models.CharField(blank=True, default="", max_length=100, verbose_name="客户姓名")),
                ("customer_phone", models.CharField(blank=True, default="", max_length=20, verbose_name="客户电话")),
                ("sales_channel", models.CharField(choices=[("store", "门店"), ("online", "线上"), ("wholesale", "批发")], default="store", max_length=20, verbose_name="销售渠道")),
                ("payment_method", models.CharField(choices=[("cash", "现金"), ("wechat", "微信支付"), ("alipay", "支付宝"), ("card", "银行卡"), ("unionpay", "云闪付")], default="cash", max_length=20, verbose_name="支付方式")),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name="总金额")),
                ("discount_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name="优惠金额")),
                ("actual_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name="实收金额")),
                ("sales_time", models.DateTimeField(verbose_name="销售时间")),
                ("cashier", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sales_records", to=settings.AUTH_USER_MODEL, verbose_name="收银员")),
                ("create_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="创建人")),
                ("update_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="更新人")),
            ],
            options={
                "verbose_name": "销售记录",
                "verbose_name_plural": "销售记录管理",
                "ordering": ["-sales_time"],
            },
        ),
        migrations.CreateModel(
            name="CashImportRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("create_time", models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name="创建时间")),
                ("update_time", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("remark", models.TextField(blank=True, default="", verbose_name="备注")),
                ("code", models.CharField(db_index=True, max_length=50, unique=True, verbose_name="编码")),
                ("name", models.CharField(max_length=100, verbose_name="名称")),
                ("file_name", models.CharField(max_length=200, verbose_name="文件名")),
                ("file_size", models.IntegerField(verbose_name="文件大小(B)")),
                ("import_type", models.CharField(default="sales", max_length=20, verbose_name="导入类型")),
                ("status", models.CharField(choices=[("pending", "待处理"), ("processing", "处理中"), ("completed", "已完成"), ("failed", "失败")], default="pending", max_length=20, verbose_name="状态")),
                ("total_records", models.IntegerField(default=0, verbose_name="总记录数")),
                ("success_count", models.IntegerField(default=0, verbose_name="成功数")),
                ("fail_count", models.IntegerField(default=0, verbose_name="失败数")),
                ("error_message", models.TextField(blank=True, default="", verbose_name="错误信息")),
                ("import_time", models.DateTimeField(auto_now_add=True, verbose_name="导入时间")),
                ("create_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="创建人")),
                ("import_user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="cash_imports", to=settings.AUTH_USER_MODEL, verbose_name="导入用户")),
                ("update_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="更新人")),
            ],
            options={
                "verbose_name": "收银数据导入记录",
                "verbose_name_plural": "收银数据导入记录管理",
                "ordering": ["-import_time"],
            },
        ),
        migrations.CreateModel(
            name="SalesAnalysis",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("create_time", models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name="创建时间")),
                ("update_time", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("status", models.IntegerField(choices=[(0, "停用"), (1, "启用"), (2, "已删除")], default=1, verbose_name="状态")),
                ("remark", models.TextField(blank=True, default="", verbose_name="备注")),
                ("analysis_date", models.DateField(db_index=True, unique=True, verbose_name="分析日期")),
                ("total_sales", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="总销售额")),
                ("total_orders", models.IntegerField(default=0, verbose_name="总订单数")),
                ("total_products", models.IntegerField(default=0, verbose_name="总商品数")),
                ("avg_order_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="平均订单金额")),
                ("best_selling_product", models.CharField(blank=True, default="", max_length=200, verbose_name="热销商品")),
                ("best_selling_count", models.IntegerField(default=0, verbose_name="热销数量")),
                ("analysis_time", models.DateTimeField(auto_now=True, verbose_name="分析时间")),
                ("create_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="创建人")),
                ("update_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="更新人")),
            ],
            options={
                "verbose_name": "销售分析",
                "verbose_name_plural": "销售分析管理",
                "ordering": ["-analysis_date"],
            },
        ),
        migrations.CreateModel(
            name="SalesItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("create_time", models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name="创建时间")),
                ("update_time", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("status", models.IntegerField(choices=[(0, "停用"), (1, "启用"), (2, "已删除")], default=1, verbose_name="状态")),
                ("remark", models.TextField(blank=True, default="", verbose_name="备注")),
                ("quantity", models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name="数量")),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name="单价")),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name="小计")),
                ("create_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="创建人")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sales_items", to="products.product", verbose_name="商品")),
                ("sales_record", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="operations.salesrecord", verbose_name="销售记录")),
                ("update_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_%(class)s", to=settings.AUTH_USER_MODEL, verbose_name="更新人")),
            ],
            options={
                "verbose_name": "销售明细",
                "verbose_name_plural": "销售明细管理",
                "ordering": ["-create_time"],
            },
        ),
    ]
