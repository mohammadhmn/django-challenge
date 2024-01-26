from rest_framework import serializers


class ReserveSeatSerializer(serializers.Serializer):
    match = serializers.IntegerField()
    seat = serializers.IntegerField()
