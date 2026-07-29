from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    default_app_config = 'apps.users.apps.UsersConfig'
    name = 'apps.users'
    verbose_name = '用户管理'