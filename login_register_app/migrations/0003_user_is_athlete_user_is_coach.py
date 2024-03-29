# Generated by Django 4.1.5 on 2023-02-14 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_register_app', '0002_user_is_active_user_is_staff_user_is_superuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_athlete',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_coach',
            field=models.BooleanField(default=False),
        ),
    ]
