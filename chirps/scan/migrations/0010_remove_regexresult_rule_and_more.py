# Generated by Django 4.2.3 on 2023-08-28 14:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('scan', '0009_merge_20230825_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='regexresult',
            name='rule',
        ),
        migrations.RemoveField(
            model_name='regexresult',
            name='scan_asset',
        ),
        migrations.DeleteModel(
            name='RegexFinding',
        ),
        migrations.DeleteModel(
            name='RegexResult',
        ),
    ]
