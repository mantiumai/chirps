# Generated by Django 4.2.3 on 2023-08-29 19:24

import django.db.models.deletion
import fernet_fields.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scan', '0011_merge_20230828_1433'),
        ('policy', '0007_delete_outcome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regexresult',
            name='scan_asset',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='regex_results',
                to='scan.scanasset',
            ),
        ),
        migrations.CreateModel(
            name='MultiQueryResult',
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
                ('conversation', fernet_fields.fields.EncryptedTextField()),
                (
                    'rule',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='policy.multiqueryrule',
                    ),
                ),
                (
                    'scan_asset',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='multiquery_results',
                        to='scan.scanasset',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MultiQueryFinding',
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
                ('attacker_question', fernet_fields.fields.EncryptedTextField()),
                ('target_response', fernet_fields.fields.EncryptedTextField()),
                (
                    'result',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='findings',
                        to='policy.multiqueryresult',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]