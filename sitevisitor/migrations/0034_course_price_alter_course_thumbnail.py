# Generated by Django 5.1.2 on 2024-11-09 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisitor', '0033_course_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='thumbnail',
            field=models.ImageField(blank=True, default='course_thumbnails/default_thumbnail.jpg', null=True, upload_to='course_thumbnails/'),
        ),
    ]
