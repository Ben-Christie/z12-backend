from rest_framework import serializers

class ErgMetricsSerializer(serializers.Serializer):
    distance = serializers.CharField()
    strokes_per_minute = serializers.IntegerField()
    split_500m = serializers.DurationField()
    time = serializers.DurationField()

class SAndCMetricsSerializer(serializers.Serializer):
    exercise = serializers.CharField()
    weight = serializers.IntegerField()
    reps = serializers.IntegerField()
    exercise_list = serializers.ListField(child = serializers.CharField(), required = False)