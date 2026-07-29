from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplier",
            name="credit_rating",
            field=models.IntegerField(default=3, verbose_name="信用等级"),
        ),
    ]
