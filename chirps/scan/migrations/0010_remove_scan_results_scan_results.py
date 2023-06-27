# Generated by Django 4.2.2 on 2023-06-27 16:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scan", "0009_remove_result_details_result_count"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="scan",
            name="results",
        ),
        migrations.AddField(
            model_name="scan",
            name="results",
            field=models.ManyToManyField(blank=True, to="scan.result"),
        ),
    ]