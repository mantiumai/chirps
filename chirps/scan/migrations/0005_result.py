# Generated by Django 4.2.2 on 2023-06-27 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("plan", "0004_alter_rule_plan"),
        ("scan", "0004_scan_plan"),
    ]

    operations = [
        migrations.CreateModel(
            name="Result",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("result", models.BooleanField()),
                (
                    "rule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="plan.rule"
                    ),
                ),
            ],
        ),
    ]
