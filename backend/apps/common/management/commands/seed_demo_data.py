from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.operations.models import OperationLog, SalesItem, SalesRecord
from apps.products.models import Category, Product, ProductInventory, Supplier, Warehouse


class Command(BaseCommand):
    help = "生成毕业设计演示用的基础数据"

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin = self._upsert_user(
            user_model,
            username="admin",
            password="123456",
            employee_id="EMP0001",
            role=user_model.Role.SUPER_ADMIN,
            phone="13800000001",
            department="系统管理",
            position="超级管理员",
            is_superuser=True,
            is_staff=True,
        )
        inventory_manager = self._upsert_user(
            user_model,
            username="stock_admin",
            password="123456",
            employee_id="EMP0002",
            role=user_model.Role.INVENTORY_MANAGER,
            phone="13800000002",
            department="仓储部",
            position="库存管理员",
            is_staff=True,
        )
        self._upsert_user(
            user_model,
            username="finance",
            password="123456",
            employee_id="EMP0003",
            role=user_model.Role.FINANCE,
            phone="13800000003",
            department="财务部",
            position="财务专员",
            is_staff=True,
        )
        cashier = self._upsert_user(
            user_model,
            username="cashier",
            password="123456",
            employee_id="EMP0004",
            role=user_model.Role.CASHIER,
            phone="13800000004",
            department="门店",
            position="收银员",
        )

        beverage = self._upsert_category("CAT001", "饮料酒水", 1, admin)
        snacks = self._upsert_category("CAT002", "休闲零食", 2, admin)
        daily = self._upsert_category("CAT003", "日用百货", 3, admin)

        supplier_a = self._upsert_supplier(
            code="SUP001",
            name="华北食品供应商",
            contact_person="张强",
            phone="13900000001",
            address="北京市朝阳区物流园 18 号",
            email="supplier1@example.com",
            credit_rating=5,
            create_by=admin,
        )
        supplier_b = self._upsert_supplier(
            code="SUP002",
            name="社区百货配送中心",
            contact_person="李静",
            phone="13900000002",
            address="北京市海淀区仓储路 6 号",
            email="supplier2@example.com",
            credit_rating=4,
            create_by=admin,
        )

        main_warehouse = self._upsert_warehouse(
            code="WH001",
            name="主仓库",
            address="一层后仓",
            manager=inventory_manager,
            contact_phone="010-88886666",
            create_by=admin,
        )
        backup_warehouse = self._upsert_warehouse(
            code="WH002",
            name="前置仓",
            address="卖场补货区",
            manager=inventory_manager,
            contact_phone="010-88889999",
            create_by=admin,
        )

        cola = self._upsert_product(
            code="P001",
            name="可口可乐 500ml",
            barcode="6900000000001",
            category=beverage,
            supplier=supplier_a,
            purchase_price=Decimal("2.50"),
            sale_price=Decimal("3.50"),
            min_stock=30,
            max_stock=200,
            brand="可口可乐",
            specification="500ml/瓶",
            create_by=admin,
        )
        milk = self._upsert_product(
            code="P002",
            name="纯牛奶 250ml",
            barcode="6900000000002",
            category=beverage,
            supplier=supplier_a,
            purchase_price=Decimal("2.80"),
            sale_price=Decimal("4.20"),
            min_stock=20,
            max_stock=150,
            brand="伊利",
            specification="250ml/盒",
            create_by=admin,
        )
        chips = self._upsert_product(
            code="P003",
            name="薯片原味 70g",
            barcode="6900000000003",
            category=snacks,
            supplier=supplier_b,
            purchase_price=Decimal("3.20"),
            sale_price=Decimal("5.00"),
            min_stock=40,
            max_stock=160,
            brand="乐事",
            specification="70g/袋",
            create_by=admin,
        )
        tissue = self._upsert_product(
            code="P004",
            name="抽纸 3 层 120 抽",
            barcode="6900000000004",
            category=daily,
            supplier=supplier_b,
            purchase_price=Decimal("7.50"),
            sale_price=Decimal("10.00"),
            min_stock=15,
            max_stock=80,
            brand="清风",
            specification="3 层 120 抽",
            create_by=admin,
        )

        self._upsert_inventory(cola, main_warehouse, 18)
        self._upsert_inventory(milk, main_warehouse, 56)
        self._upsert_inventory(chips, main_warehouse, 72)
        self._upsert_inventory(tissue, main_warehouse, 12)
        self._upsert_inventory(cola, backup_warehouse, 24)
        self._upsert_inventory(chips, backup_warehouse, 20)

        self._upsert_sales_record(
            order_number="SALEDEMO001",
            cashier=cashier,
            items=[
                {"product": cola, "quantity": 3, "unit_price": Decimal("3.50")},
                {"product": chips, "quantity": 2, "unit_price": Decimal("5.00")},
            ],
            customer_name="王敏",
            customer_phone="13600000001",
        )
        self._upsert_sales_record(
            order_number="SALEDEMO002",
            cashier=cashier,
            items=[
                {"product": milk, "quantity": 4, "unit_price": Decimal("4.20")},
                {"product": tissue, "quantity": 1, "unit_price": Decimal("10.00")},
            ],
            customer_name="陈亮",
            customer_phone="13600000002",
        )

        self._ensure_log(
            user=admin,
            action_type=OperationLog.ActionType.CREATE,
            model_name="Product",
            object_id=str(cola.id),
            object_repr=str(cola),
            action_detail="初始化演示商品数据",
        )
        self._ensure_log(
            user=inventory_manager,
            action_type=OperationLog.ActionType.INVENTORY_IN,
            model_name="ProductInventory",
            object_id=str(cola.id),
            object_repr=f"{cola.name} - 主仓库",
            action_detail="初始化库存数据，便于演示入库/出库与预警",
        )
        self._ensure_log(
            user=cashier,
            action_type=OperationLog.ActionType.SALE,
            model_name="SalesRecord",
            object_id="SALEDEMO001",
            object_repr="SALEDEMO001",
            action_detail="初始化销售演示订单",
        )

        self.stdout.write(self.style.SUCCESS("演示数据初始化完成"))
        self.stdout.write("默认账号: admin / 123456")
        self.stdout.write("库存管理员: stock_admin / 123456")
        self.stdout.write("财务账号: finance / 123456")
        self.stdout.write("收银账号: cashier / 123456")

    def _upsert_user(self, user_model, username, password, **extra_fields):
        defaults = {**extra_fields, "status": 1}
        user, created = user_model.objects.get_or_create(username=username, defaults=defaults)
        changed = False
        for key, value in defaults.items():
            if getattr(user, key) != value:
                setattr(user, key, value)
                changed = True
        if created or not user.check_password(password):
            user.set_password(password)
            changed = True
        if changed:
            user.save()
        return user

    def _upsert_category(self, code, name, sort_order, user):
        category, _ = Category.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "sort_order": sort_order,
                "status": 1,
                "create_by": user,
                "update_by": user,
            },
        )
        return category

    def _upsert_supplier(self, **kwargs):
        code = kwargs.pop("code")
        name = kwargs.pop("name")
        supplier, _ = Supplier.objects.update_or_create(
            code=code,
            defaults={"name": name, "status": 1, **kwargs},
        )
        return supplier

    def _upsert_warehouse(self, **kwargs):
        code = kwargs.pop("code")
        name = kwargs.pop("name")
        warehouse, _ = Warehouse.objects.update_or_create(
            code=code,
            defaults={"name": name, "status": 1, **kwargs},
        )
        return warehouse

    def _upsert_product(self, **kwargs):
        code = kwargs.pop("code")
        name = kwargs.pop("name")
        product, _ = Product.objects.update_or_create(
            code=code,
            defaults={"name": name, "status": 1, "unit": "piece", **kwargs},
        )
        return product

    def _upsert_inventory(self, product, warehouse, current_stock):
        ProductInventory.objects.update_or_create(
            product=product,
            warehouse=warehouse,
            defaults={
                "current_stock": current_stock,
                "locked_stock": 0,
                "warning_sent": False,
            },
        )

    def _upsert_sales_record(self, order_number, cashier, items, customer_name="", customer_phone=""):
        total_amount = sum(item["quantity"] * item["unit_price"] for item in items)
        sales_record, _ = SalesRecord.objects.update_or_create(
            order_number=order_number,
            defaults={
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "sales_channel": SalesRecord.SalesChannel.STORE,
                "payment_method": SalesRecord.PaymentMethod.CASH,
                "total_amount": total_amount,
                "discount_amount": Decimal("0.00"),
                "actual_amount": total_amount,
                "cashier": cashier,
                "remark": "演示订单",
                "sales_time": timezone.now(),
            },
        )
        sales_record.items.all().delete()
        for item in items:
            SalesItem.objects.create(
                sales_record=sales_record,
                product=item["product"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["quantity"] * item["unit_price"],
            )
        return sales_record

    def _ensure_log(self, user, action_type, model_name, object_id, object_repr, action_detail):
        OperationLog.objects.get_or_create(
            user=user,
            action_type=action_type,
            model_name=model_name,
            object_id=object_id,
            defaults={
                "object_repr": object_repr,
                "action_detail": action_detail,
                "ip_address": "127.0.0.1",
                "user_agent": "seed_demo_data",
            },
        )
