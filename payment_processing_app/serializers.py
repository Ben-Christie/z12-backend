from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    card_number = serializers.CharField()
    expiry_date = serializers.CharField()
    cvv = serializers.CharField()
    title = serializers.CharField()
    total_amount = serializers.CharField()