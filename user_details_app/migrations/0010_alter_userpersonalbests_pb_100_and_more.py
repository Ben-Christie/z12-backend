# Generated by Django 4.1.5 on 2023-03-18 23:37

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_details_app', '0009_remove_userrowinginfo_development_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_100',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_1000',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_10000',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_2000',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_500',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_6000',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='userrowinginfo',
            name='clubs',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='userrowinginfo',
            name='coaches',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='userrowinginfo',
            name='race_category',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
