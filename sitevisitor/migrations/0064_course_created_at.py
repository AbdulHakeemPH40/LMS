# Generated by Django 5.1.2 on 2024-11-15 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisitor', '0063_remove_promotion_created_at_promotion_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
