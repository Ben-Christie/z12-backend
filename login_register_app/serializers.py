from rest_framework import serializers
from .models import User
import datetime

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
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
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'