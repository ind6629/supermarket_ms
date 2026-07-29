"""
用户管理模型
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from apps.common.models import BaseModel


class User(AbstractUser, BaseModel):
    """
    用户模型
    继承Django内置的AbstractUser，添加自定义字段
    """
    
    class Role(models.IntegerChoices):
        """用户角色枚举"""
        SUPER_ADMIN = 0, '超级管理员'
        ADMIN = 1, '管理员'
        INVENTORY_MANAGER = 2, '库存管理员'
        FINANCE = 3, '财务人员'
        CASHIER = 4, '收银员'
    
    class Gender(models.IntegerChoices):
        """性别枚举"""
        MALE = 0, '男'
        FEMALE = 1, '女'
        UNKNOWN = 2, '未知'

    class ApprovalStatus(models.IntegerChoices):
        """注册审核状态"""
        PENDING = 0, '待审核'
        APPROVED = 1, '已通过'
        REJECTED = 2, '已驳回'
    
    phone_regex = RegexValidator(
        regex=r'^1[3-9]\d{9}$',
        message="手机号码格式不正确，应为11位数字并以1开头"
    )
    
    # 扩展字段
    employee_id = models.CharField('工号', max_length=20, unique=True, db_index=True)
    role = models.IntegerField('角色', choices=Role.choices, default=Role.CASHIER)
    phone = models.CharField('手机号', max_length=11, validators=[phone_regex], unique=True, db_index=True)
    gender = models.IntegerField('性别', choices=Gender.choices, default=Gender.UNKNOWN)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    department = models.CharField('部门', max_length=50, blank=True, default='')
    position = models.CharField('职位', max_length=50, blank=True, default='')
    last_login_ip = models.GenericIPAddressField('最后登录IP', null=True, blank=True)
    last_login_time = models.DateTimeField('最后登录时间', null=True, blank=True)
    password_changed_time = models.DateTimeField('密码修改时间', null=True, blank=True)
    login_failures = models.IntegerField('登录失败次数', default=0)
    locked_until = models.DateTimeField('锁定至', null=True, blank=True)
    approval_status = models.IntegerField('审核状态', choices=ApprovalStatus.choices, default=ApprovalStatus.APPROVED)
    review_remark = models.CharField('审核备注', max_length=200, blank=True, default='')
    review_time = models.DateTimeField('审核时间', null=True, blank=True)
    
    # 覆盖父类的字段
    email = models.EmailField('邮箱', blank=True, null=True, unique=True)
    first_name = None
    last_name = None
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['department', 'status']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def set_password(self, raw_password):
        """设置密码并记录修改时间"""
        self.password = make_password(raw_password)
        self.password_changed_time = timezone.now()
        self.login_failures = 0
        self.locked_until = None
    
    def check_login_attempts(self):
        """检查登录尝试，如果失败次数过多则锁定"""
        if self.locked_until and self.locked_until > timezone.now():
            raise Exception(f"账户已被锁定，请于 {self.locked_until.strftime('%Y-%m-%d %H:%M:%S')} 后重试")
    
    def record_login_success(self, ip_address):
        """记录登录成功"""
        self.last_login = timezone.now()
        self.last_login_ip = ip_address
        self.last_login_time = timezone.now()
        self.login_failures = 0
        self.locked_until = None
        self.save(update_fields=[
            'last_login', 'last_login_ip', 'last_login_time', 
            'login_failures', 'locked_until'
        ])
    
    def record_login_failure(self):
        """记录登录失败"""
        self.login_failures += 1
        if self.login_failures >= 5:  # 连续失败5次锁定1小时
            self.locked_until = timezone.now() + timezone.timedelta(hours=1)
        self.save(update_fields=['login_failures', 'locked_until'])
    
    def reset_password(self, new_password, reset_by=None):
        """重置密码"""
        self.set_password(new_password)
        if reset_by:
            self.update_by = reset_by
        self.save(update_fields=['password', 'password_changed_time', 'update_by', 'update_time'])
    
    def get_full_name(self):
        """获取用户全名"""
        return self.username
    
    def get_short_name(self):
        """获取用户简称"""
        return self.username


class UserGroup(models.Model):
    """
    用户组（角色分组）
    """
    name = models.CharField('组名', max_length=50, unique=True)
    code = models.CharField('组代码', max_length=50, unique=True, db_index=True)
    description = models.TextField('描述', blank=True, default='')
    members = models.ManyToManyField(User, verbose_name='组成员', related_name='custom_groups', blank=True)
    permissions = models.TextField('权限列表', help_text='JSON格式的权限列表', blank=True, default='[]')
    create_time = models.DateTimeField('创建时间', default=timezone.now, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    status = models.IntegerField('状态', choices=BaseModel.Status.choices, default=BaseModel.Status.ACTIVE)
    
    class Meta:
        verbose_name = '用户组'
        verbose_name_plural = '用户组管理'
        ordering = ['-create_time']
    
    def __str__(self):
        return self.name