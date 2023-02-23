from django.db import models

GENDER_OPTIONS = [
  ('Male', 'Male'),
  ('Female', 'Female')
]

class ClubInfo(models.Model):
  club_id = models.AutoField(primary_key=True)
  club_name = models.CharField(max_length=100)
  club_nickname = models.CharField(max_length=100)

  class Meta:
        db_table = 'rowing_club_info'

class RaceCategory(models.Model):
  category_id = models.AutoField(primary_key=True)
  category = models.CharField(max_length=100)
  max_age = models.IntegerField()
  required_gender = models.CharField(max_length=6, choices=GENDER_OPTIONS, null=True)
  max_weight = models.IntegerField()

  class Meta:
    db_table = 'race_categories'