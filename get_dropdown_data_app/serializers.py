from rest_framework import serializers

class ClubInfoSerializer(serializers.Serializer):
  club_name = serializers.CharField()
  club_nickname = serializers.CharField()

class RaceCategorySerializer(serializers.Serializer):
  category = serializers.CharField()
  max_age = serializers.IntegerField()
  required_gender = serializers.CharField()
  max_weight = serializers.IntegerField()
  category_nickname = serializers.CharField()