# Generated by Django 4.2.2 on 2023-07-12 13:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("target", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="redistarget",
            name="embedding_field",
            field=models.CharField(default="embedding", max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="redistarget",
            name="index_name",
            field=models.CharField(default="index", max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="redistarget",
            name="text_field",
            field=models.CharField(default="content", max_length=256),
            preserve_default=False,
        ),
    ]
