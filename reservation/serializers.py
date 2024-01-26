from rest_framework import serializers


class ReserveSeatSerializer(serializers.Serializer):
    """
    Serializer for reserving a seat in a match.

    ---
    # Fields
    - `match`: The ID of the match.
    - `seat`: The seat number to be reserved.
    """

    match = serializers.IntegerField()
    seat = serializers.IntegerField()
