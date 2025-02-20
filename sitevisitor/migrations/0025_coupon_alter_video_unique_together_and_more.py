# Generated by Django 5.1.2 on 2024-11-07 13:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisitor', '0024_alter_comment_course_alter_comment_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_percentage', models.DecimalField(decimal_places=2, help_text='Discount percentage (e.g., 10 for 10%)', max_digits=5, validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(100.0)])),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('active', models.BooleanField(default=True)),
                ('usage_limit', models.PositiveIntegerField(blank=True, help_text='Total number of times this coupon can be used.', null=True)),
                ('times_used', models.PositiveIntegerField(default=0, help_text='Number of times the coupon has been used.')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='video',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='video',
            name='course',
        ),
        migrations.DeleteModel(
            name='CourseContent',
        ),
        migrations.DeleteModel(
            name='Video',
        ),
    ]
