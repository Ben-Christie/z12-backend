from rest_framework import serializers
from login_register_app.models import User

class DetailsModalSerializer(serializers.Serializer):
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    date_of_birth = serializers.CharField(required = True)
    gender = serializers.CharField(required = True)
    phone_number = serializers.CharField(required = False)
    athlete_or_coach = serializers.CharField(required = True)
    weight = serializers.CharField(required = False)
    height = serializers.CharField(required = False)
    wingspan = serializers.CharField(required = False)
    race_category = serializers.CharField(required = False)
    clubs = serializers.ListField(child = serializers.CharField(), required = False)
    coaches = serializers.ListField(child = serializers.CharField(), required=False)
