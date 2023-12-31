# Generated by Django 4.2.3 on 2023-08-28 14:00

import django.db.models.deletion
import fernet_fields.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scan', '0010_remove_regexresult_rule_and_more'),
        ('policy', '0004_delete_rule_baserule_policy_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegexResult',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('text', fernet_fields.fields.EncryptedTextField()),
                (
                    'rule',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='policy.regexrule',
                    ),
                ),
                (
                    'scan_asset',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='results',
                        to='scan.scanasset',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RegexFinding',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('source_id', models.TextField(blank=True, null=True)),
                ('offset', models.IntegerField()),
                ('length', models.IntegerField()),
                (
                    'result',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='findings',
                        to='policy.regexresult',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
