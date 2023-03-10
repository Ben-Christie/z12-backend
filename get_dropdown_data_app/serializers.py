from rest_framework import serializers

class ClubInfoSerializer(serializers.Serializer):
  club_name = serializers.CharField()
  club_nickname = serializers.CharField()

class RaceCategorySerializer(serializers.Serializer):
  category = serializers.CharField(required = False)
  max_age = serializers.IntegerField(required = False)
  required_gender = serializers.CharField(required = False)
  max_weight = serializers.IntegerField(required = False)
  category_nickname = serializers.CharField(required = False)