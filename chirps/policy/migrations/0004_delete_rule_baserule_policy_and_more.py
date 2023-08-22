# Generated by Django 4.2.3 on 2023-08-21 14:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('policy', '0003_baserule_remove_rule_policy_remove_rule_severity_and_more'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('severity', '0001_initial'),
        ('scan', '0007_alter_result_rule'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Rule',
        ),
        migrations.AddField(
            model_name='baserule',
            name='policy',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rules',
                to='policy.policyversion',
            ),
        ),
        migrations.AddField(
            model_name='baserule',
            name='polymorphic_ctype',
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='polymorphic_%(app_label)s.%(class)s_set+',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='baserule',
            name='severity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='severity.severity'),
        ),
    ]
