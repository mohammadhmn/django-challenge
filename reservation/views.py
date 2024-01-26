from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from matches import facade as matches_facade
from matches.models import Match, Seat
from reservation.models import Reservation
from reservation.serializers import ReserveSeatSerializer


class ReserveSeatView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request: Request):
        serializer = ReserveSeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        match, response = self._get_match_or_error(serializer.validated_data["match"])
        if response:
            return response

        seat, response = self._get_seat_or_error(serializer.validated_data["seat"])
        if response:
            return response

        reservation = Reservation.objects.create(user=user, match=match, seat=seat)

        try:
            matches_facade.safe_reserve_seat_by_id(
                id=seat.id,
                updated_at=seat.updated_at,
            )
        except IntegrityError:
            reservation.delete()
            return Response(
                {"error": "Concurrent update detected. Please try again."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"message": "Successfully reserved the seat"},
            status=status.HTTP_201_CREATED,
        )

    def _get_match_or_error(
        self, match_id: int
    ) -> tuple[Match | None, Response | None]:
        match = matches_facade.get_match_by_id(match_id)
        if not match:
            return None, Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return match, None

    def _get_seat_or_error(self, seat_id: int) -> tuple[Seat | None, Response | None]:
        seat = matches_facade.get_unreserved_seat_by_id(seat_id)
        if not seat:
            return None, Response(
                {"error": "Seat is reserved or not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return seat, None
