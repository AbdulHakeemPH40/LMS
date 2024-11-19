# Generated by Django 5.1.2 on 2024-11-12 15:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisitor', '0045_coupon_course_coupon_user_alter_coupon_times_used'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='discount_percentage',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='user',
        ),
        migrations.AlterField(
            model_name='coupon',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sitevisitor.course'),
        ),
    ]
