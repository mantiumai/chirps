# Generated by Django 4.2.3 on 2023-08-21 14:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('policy', '0003_baserule_remove_rule_policy_remove_rule_severity_and_more'),
        ('scan', '0006_alter_scanasset_asset_alter_scanasset_scan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='policy.regexrule'),
        ),
    ]
