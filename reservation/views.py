from django.db import IntegrityError, transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
    """
    View for reserving a seat in a match.

    ---
    # Permissions
    - User must be authenticated.

    # Request Body
    - `match`: The ID of the match.
    - `seat`: The seat number to be reserved.

    # Responses
    - 201 Created: Successfully reserved the seat.
    - 400 Bad Request: Invalid request data or seat is reserved/not available.
    - 404 Not Found: Match not found.
    - 409 Conflict: Concurrent update detected. Please try again.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "match": openapi.Schema(type=openapi.TYPE_INTEGER),
                "seat": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=["match", "seat"],
        ),
        responses={
            201: "Successfully reserved the seat.",
            400: "Bad Request. Invalid request data or seat is reserved/not available.",
            404: "Not Found. Match not found.",
            409: "Conflict. Concurrent update detected. Please try again.",
        },
    )
    def post(self, request: Request):
        """
        Reserve a seat in a match.

        :param request: The HTTP request object.
        :type request: Request
        :return: The HTTP response object.
        :rtype: Response
        """
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
        """
        Get a match by its ID or return a 404 response if not found.

        :param match_id: The ID of the match.
        :type match_id: int
        :return: A tuple containing the match and a 404 response or None.
        :rtype: tuple[Match, Response]
        """
        match = matches_facade.get_match_by_id(match_id)
        if not match:
            return None, Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return match, None

    def _get_seat_or_error(self, seat_id: int) -> tuple[Seat | None, Response | None]:
        """
        Get an unreserved seat by its ID or return a 400 response if not available.

        :param seat_id: The ID of the seat.
        :type seat_id: int
        :return: A tuple containing the seat and a 400 response or None.
        :rtype: tuple[Seat, Response]
        """
        seat = matches_facade.get_unreserved_seat_by_id(seat_id)
        if not seat:
            return None, Response(
                {"error": "Seat is reserved or not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return seat, None
