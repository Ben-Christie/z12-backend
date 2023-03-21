from rest_framework import serializers

class ErgMetricsSerializer(serializers.Serializer):
    distance = serializers.CharField()
    strokes_per_minute = serializers.IntegerField()
    split_500m = serializers.CharField(required = False)
    time = serializers.CharField()
    time_in_seconds = serializers.FloatField(required = False)
    intensity_percentage = serializers.IntegerField(required = False)
    date = serializers.DateField(required = False)

class SAndCMetricsSerializer(serializers.Serializer):
    exercise = serializers.CharField()
    weight = serializers.IntegerField()
    reps = serializers.IntegerField()
    exercise_list = serializers.ListField(child = serializers.CharField(), required = False)
    date = serializers.DateField(required = False)