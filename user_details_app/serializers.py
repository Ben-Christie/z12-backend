from rest_framework import serializers

class CoreDetailsSerializer(serializers.Serializer):
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField()
    date_of_birth = serializers.CharField()
    gender = serializers.CharField()
    phone_number = serializers.CharField()
    athlete_or_coach = serializers.CharField()
    is_athlete = serializers.BooleanField(default = True)
    is_coach = serializers.BooleanField(default = False)

class AthleteDetailsSerializer(serializers.Serializer):
    clubs = serializers.ListField(child = serializers.CharField(), required=False)
    coaches = serializers.ListField(child = serializers.CharField(), required=False)
    race_category = serializers.CharField(required=False, allow_blank=True)
    weight = serializers.CharField(required=False, allow_blank=True)
    height = serializers.CharField(required=False, allow_blank=True)
    wingspan = serializers.CharField(required=False, allow_blank=True)

class PersonalBestsSerializer(serializers.Serializer):
    pb_100 = serializers.DurationField()
    pb_500 = serializers.DurationField()
    pb_1000 = serializers.DurationField(required=False)
    pb_2000 = serializers.DurationField(required=False)
    pb_6000 = serializers.DurationField(required=False)
    pb_10000 = serializers.DurationField(required=False)