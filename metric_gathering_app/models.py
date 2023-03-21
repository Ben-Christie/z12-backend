from django.db import models
from login_register_app.models import User


class UserErgMetrics(models.Model):
    erg_metric_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    distance = models.CharField(max_length=10)
    strokes_per_minute = models.IntegerField(null=True)
    split_500m = models.CharField(max_length=20)
    time = models.CharField(max_length=20)
    time_in_seconds = models.FloatField()
    intensity_percentage = models.IntegerField()
    date = models.DateField(auto_now=True)

    class Meta:
        db_table = 'user_erg_metrics'

class UserSAndCMetrics(models.Model):
    s_and_c_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.CharField(max_length=50)
    weight = models.IntegerField()
    reps = models.IntegerField()
    date = models.DateField(auto_now=True)

    class Meta:
        db_table = 'user_s_and_c_metrics'