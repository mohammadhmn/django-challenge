from django.core.exceptions import ValidationError
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from matches.models import Match, Seat


class MatchSerializer(serializers.ModelSerializer):
    """
    Serializer for the Match model.

    ---
    # Fields
    - `id`: The unique identifier for the match.
    - `stadium`: The stadium where the match is held.
    - `home_side`: The home side participating in the match.
    - `away_side`: The away side participating in the match.
    - `match_day`: The day on which the match takes place.
    - `match_time`: The time at which the match starts.

    # Validations
    - Home and away sides should be different.
    - Check if home or away sides have a match on the selected match day and time.
    - Check if the stadium is busy on the selected match day and time.
    """

    class Meta:
        model = Match
        fields = ["id", "stadium", "home_side", "away_side", "match_day", "match_time"]

    def validate(self, data):
        self._validate_sides(data)
        self._validate_stadium(data)
        return super().validate(data)

    def _validate_sides(self, data):
        """
        Validate that home and away sides are different and not already occupied.

        :param data: The data to be validated.
        :type data: dict
        :raises ValidationError: If validation fails.
        """
        home_side = data.get("home_side")
        away_side = data.get("away_side")
        match_day = data.get("match_day")
        match_time = data.get("match_time")

        if home_side == away_side:
            raise ValidationError("Home and away sides are the same")

        sides_have_match = Match.objects.filter(
            Q(home_side=home_side)
            | Q(away_side=home_side)
            | Q(home_side=away_side)
            | Q(away_side=away_side),
            match_day=match_day,
            match_time=match_time,
        ).exists()
        if sides_have_match:
            raise ValidationError(
                "Home side or away side have a match on the selected match day and time"
            )

    def _validate_stadium(self, data):
        """
        Validate that the stadium is not busy on the selected match day and time.

        :param data: The data to be validated.
        :type data: dict
        :raises ValidationError: If validation fails.
        """
        match_day = data.get("match_day")
        match_time = data.get("match_time")
        stadium = data.get("stadium")

        is_stadium_busy = Match.objects.filter(
            stadium=stadium,
            match_day=match_day,
            match_time=match_time,
        ).exists()
        if is_stadium_busy:
            raise ValidationError("Stadium is busy on the selected match day and time")


class SeatSerializer(serializers.ModelSerializer):
    """
    Serializer for the Seat model.

    ---
    # Fields
    - `id`: The unique identifier for the seat.
    - `match`: The match to which the seat belongs.
    - `seat_number`: The seat number.
    - `is_reserved`: Indicates whether the seat is reserved.
    """

    class Meta:
        model = Seat
        fields = ["id", "match", "seat_number", "is_reserved"]
