# Generated by Django 4.2.3 on 2023-07-05 16:14

import fernet_fields.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("target", "0002_pineconetarget"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pineconetarget",
            name="api_key",
            field=fernet_fields.fields.EncryptedCharField(max_length=256),
        ),
    ]
