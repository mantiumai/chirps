# Generated by Django 4.2.3 on 2023-09-01 19:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scan', '0012_scanrun_one_shot_celery_id_alter_scanrun_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scanrun',
            name='started_at',
            field=models.DateTimeField(),
        ),
    ]
