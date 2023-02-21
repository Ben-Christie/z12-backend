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
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_of_birth = serializers.CharField()
    gender = serializers.CharField()
    phone_number = serializers.CharField()
    athlete_or_coach = serializers.CharField()
    is_athlete = serializers.BooleanField(default=True)
    is_coach = serializers.BooleanField(default=False)

    def create(self, validated_data):
        # derive if user is athlete, coach, or both

        # pop off so not saved
        athlete_or_coach = validated_data.pop('athlete_or_coach')

        if athlete_or_coach == 'Athlete':
            validated_data['is_athlete'] = True
            validated_data['is_coach'] = False
        elif athlete_or_coach == 'Coach':
            validated_data['is_athlete'] = False
            validated_data['is_coach'] = True
        elif athlete_or_coach == 'Both':
            validated_data['is_athlete'] = True
            validated_data['is_coach'] = True

        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'