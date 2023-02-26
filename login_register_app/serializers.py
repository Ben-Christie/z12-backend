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
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'