# Generated by Django 5.1.2 on 2024-11-14 11:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisitor', '0058_alter_video_lesson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='sitevisitor.lesson'),
        ),
    ]
