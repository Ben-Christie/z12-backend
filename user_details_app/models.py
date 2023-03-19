from django.db import models
from django.contrib.postgres.fields import ArrayField
from login_register_app.models import User

class UserRowingInfo(models.Model):
    user_rowing_info_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clubs = ArrayField(models.CharField(max_length=100), null=True)
    coaches = ArrayField(models.CharField(max_length=100), null=True)
    race_category = models.CharField(max_length=50, null=True)
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    wingspan = models.IntegerField(null=True)
    class Meta:
        db_table = 'athlete_info'

class UserPersonalBests(models.Model):
    user_pb_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pb_100 = models.DurationField(null=True)
    pb_500 = models.DurationField(null=True)
    pb_1000 = models.DurationField(null=True)
    pb_2000 = models.DurationField(null=True)
    pb_6000 = models.DurationField(null=True)
    pb_10000 = models.DurationField(null=True)

    class Meta:
        db_table = 'athlete_personal_bests'

class UserProfilePicture(models.Model):
    picture_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(null = True, blank = True)

    class Meta:
        db_table = 'user_profile_pictures'
