# Generated by Django 4.1.5 on 2023-03-02 13:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_details_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfilePicture',
            fields=[
                ('picture_id', models.AutoField(primary_key=True, serialize=False)),
                ('profile_picture', models.ImageField(upload_to='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_profile_pictures',
            },
        ),
    ]
