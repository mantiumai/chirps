# Generated by Django 4.2.3 on 2023-07-20 20:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('policy', '0001_initial'),
        ('scan', '0002_remove_scan_policy_scan_policies'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='policy',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='policy.policy',
            ),
            preserve_default=False,
        ),
    ]