from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='approval_status',
            field=models.IntegerField(
                choices=[(0, '待审核'), (1, '已通过'), (2, '已驳回')],
                default=1,
                verbose_name='审核状态',
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='review_remark',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='审核备注'),
        ),
        migrations.AddField(
            model_name='user',
            name='review_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='审核时间'),
        ),
    ]
