# Generated by Django 5.1.2 on 2024-11-12 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisitor', '0042_remove_cartitem_course_remove_cartitem_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='duration_months',
        ),
        migrations.RemoveField(
            model_name='course',
            name='duration_weeks',
        ),
        migrations.AddField(
            model_name='course',
            name='duration_type',
            field=models.CharField(choices=[('month', 'Month(s)'), ('week', 'Week(s)')], default='month', help_text='Select the type of duration (Month or Week)', max_length=5),
        ),
        migrations.AddField(
            model_name='course',
            name='duration_value',
            field=models.PositiveIntegerField(default=1, help_text='Enter the number of months or weeks for the course duration'),
        ),
    ]
