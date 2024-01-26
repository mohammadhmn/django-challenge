from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from matches.models import Match, Seat
from reservation.models import Reservation


class ReserveSeatView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request: Request):
        user = request.user
        match_id = request.data.get("match")
        seat_id = request.data.get("seat")

        match = Match.objects.filter(id=match_id).first()
        if not match:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        seat = Seat.objects.filter(id=seat_id, is_reserved=False).first()
        if not seat:
            return Response(
                {"error": "Seat is reserved or not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Reservation.objects.create(
            user=user,
            match=match,
            seat=seat,
        )

        try:
            Seat.objects.filter(
                id=seat.id,
                updated_at=seat.updated_at,
            ).update(
                is_reserved=True,
            )
        except IntegrityError:
            return Response(
                {"error": "Concurrent update detected. Please try again."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"message": "Successfully reserved the seat"},
            status=status.HTTP_201_CREATED,
        )
