# Generated by Django 4.2.2 on 2023-07-01 00:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("target", "0002_remove_mantiumtarget_top_k_basetarget_top_k"),
    ]

    operations = [
        migrations.AddField(
            model_name="redistarget",
            name="index_name",
            field=models.CharField(default="", max_length=256),
            preserve_default=False,
        ),
    ]
