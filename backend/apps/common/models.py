"""
公共基础模型
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


class BaseModel(models.Model):
    """基础模型，包含所有模型的通用字段"""
    
    class Status(models.IntegerChoices):
        """状态枚举"""
        INACTIVE = 0, '停用'
        ACTIVE = 1, '启用'
        DELETED = 2, '已删除'
    
    create_time = models.DateTimeField('创建时间', default=timezone.now, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    create_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_%(class)s',
        verbose_name='创建人'
    )
    update_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='updated_%(class)s',
        verbose_name='更新人'
    )
    status = models.IntegerField('状态', choices=Status.choices, default=Status.ACTIVE)
    remark = models.TextField('备注', blank=True, default='')
    
    class Meta:
        abstract = True
        ordering = ['-create_time']
    
    def soft_delete(self, user=None):
        """软删除"""
        self.status = self.Status.DELETED
        if user:
            self.update_by = user
        self.save(update_fields=['status', 'update_by', 'update_time'])
    
    def activate(self, user=None):
        """激活"""
        self.status = self.Status.ACTIVE
        if user:
            self.update_by = user
        self.save(update_fields=['status', 'update_by', 'update_time'])
    
    def deactivate(self, user=None):
        """停用"""
        self.status = self.Status.INACTIVE
        if user:
            self.update_by = user
        self.save(update_fields=['status', 'update_by', 'update_time'])


class CodeMixin(models.Model):
    """代码/编号混合类"""
    code = models.CharField('编码', max_length=50, unique=True, db_index=True)
    name = models.CharField('名称', max_length=100)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return f"{self.code} - {self.name}"