# Generated by Django 4.1.5 on 2023-03-16 21:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_details_app', '0008_alter_userpersonalbests_pb_100_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userrowinginfo',
            name='development_rating',
        ),
    ]
