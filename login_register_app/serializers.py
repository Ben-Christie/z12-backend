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

class UserDashboardSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_of_birth = serializers.DateField()

class UserDetailsModalSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_of_birth = serializers.DateField()
    gender = serializers.CharField()
    is_athlete = serializers.BooleanField()
    is_coach = serializers.BooleanField()
    phone_number = serializers.CharField()
class AllUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'