from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers

from matches.models import Match, Seat


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["id", "stadium", "home_side", "away_side", "match_day", "match_time"]

    def validate(self, data):
        self._validate_sides(data)
        self._validate_stadium(data)
        return super().validate(data)

    def _validate_sides(self, data):
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
    class Meta:
        model = Seat
        fields = ["id", "match", "seat_number", "is_reserved"]
