# Generated by Django 5.1.2 on 2024-11-08 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisitor', '0029_alter_module_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20),
        ),
    ]
