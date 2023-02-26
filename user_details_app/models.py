from django.db import models
from django.contrib.postgres.fields import ArrayField
from login_register_app.models import User

class UserRowingInfo(models.Model):
    user_rowing_info_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club_names = ArrayField(models.CharField(max_length=100))
    coaches = ArrayField(models.CharField(max_length=100))
    race_category = models.CharField(max_length=50)
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    wingspan = models.IntegerField(null=True)
    DEVELOPMENT_OPTIONS = [
        ('Elite', 'Elite'),
        ('Pre-Elite', 'Pre-Elite'),
        ('Developmental', 'Developmental')
    ]
    development_rating = models.CharField(max_length=13, choices=DEVELOPMENT_OPTIONS, null=True)

    class Meta:
        db_table = 'athlete_info'

class UserPersonalBests(models.Model):
    user_pb_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pb_100 = models.DurationField()
    pb_500 = models.DurationField()
    pb_1000 = models.DurationField()
    pb_2000 = models.DurationField()
    pb_6000 = models.DurationField()
    pb_10000 = models.DurationField()

    class Meta:
        db_table = 'athlete_personal_bests'
