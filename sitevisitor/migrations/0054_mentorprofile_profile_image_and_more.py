# Generated by Django 5.1.2 on 2024-11-13 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisitor', '0053_alter_mentorprofile_awards_and_recognitions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorprofile',
            name='profile_image',
            field=models.ImageField(blank=True, help_text='Upload a profile image for the mentor.', null=True, upload_to='mentor_images/'),
        ),
        migrations.AlterField(
            model_name='mentorprofile',
            name='awards_and_recognitions',
            field=models.TextField(blank=True, help_text='Awards and recognitions received by the mentor.', null=True),
        ),
        migrations.AlterField(
            model_name='mentorprofile',
            name='bio',
            field=models.TextField(blank=True, help_text='Short bio of the mentor.', null=True),
        ),
        migrations.AlterField(
            model_name='mentorprofile',
            name='experience',
            field=models.TextField(blank=True, help_text="Details about the mentor's experience.", null=True),
        ),
        migrations.AlterField(
            model_name='mentorprofile',
            name='skills',
            field=models.TextField(blank=True, help_text='List of skills, separated by commas.', null=True),
        ),
    ]
