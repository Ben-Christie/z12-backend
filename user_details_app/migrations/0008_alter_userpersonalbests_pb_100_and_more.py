# Generated by Django 4.1.5 on 2023-03-16 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_details_app', '0007_alter_userpersonalbests_pb_100_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_100',
            field=models.DurationField(),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_1000',
            field=models.DurationField(),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_10000',
            field=models.DurationField(),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_2000',
            field=models.DurationField(),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_500',
            field=models.DurationField(),
        ),
        migrations.AlterField(
            model_name='userpersonalbests',
            name='pb_6000',
            field=models.DurationField(),
        ),
    ]
