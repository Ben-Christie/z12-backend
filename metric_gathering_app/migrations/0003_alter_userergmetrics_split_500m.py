# Generated by Django 4.1.5 on 2023-03-08 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metric_gathering_app', '0002_alter_userergmetrics_split_500m'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userergmetrics',
            name='split_500m',
            field=models.DurationField(),
        ),
    ]
