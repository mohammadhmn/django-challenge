from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from matches.models import Match
from matches.serializers import MatchSerializer, SeatSerializer


class BaseMatchView(APIView):
    """
    Base class for Match-related views.

    ---
    # Permissions
    - User must be authenticated.
    - User must be an admin.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = None
    model_class = None

    def _get_object_or_404(self, pk: int, error: str):
        """
        Get an object by its primary key or return a 404 response if not found.

        :param pk: Primary key of the object.
        :type pk: int
        :param error: Error message for the 404 response.
        :type error: str
        :return: A tuple containing the object and a 404 response or None.
        :rtype: tuple[object, Response]
        """
        try:
            object = self.model_class.objects.get(pk=pk)
        except Match.DoesNotExist:
            return None, Response(
                {"error": error},
                status=status.HTTP_404_NOT_FOUND,
            )

        return object, None

    def _create_response(self, data: dict, status_code: int):
        """
        Create a custom response.

        :param data: Response data.
        :type data: dict
        :param status_code: HTTP status code.
        :type status_code: int
        :return: The custom response.
        :rtype: Response
        """
        return Response(data=data, status=status_code)


class AddMatchView(BaseMatchView):
    """
    View for adding a new Match.

    # Request Body
    - `stadium`: The stadium where the match will be held.
    - `home_side`: The home side participating in the match.
    - `away_side`: The away side participating in the match.
    - `match_day`: The day on which the match will take place.
    - `match_time`: The time at which the match will start.

    # Responses
    - 201 Created: Match created successfully.
    - 400 Bad Request: Invalid request data.
    """

    serializer_class = MatchSerializer
    model_class = Match

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "stadium": openapi.Schema(type=openapi.TYPE_STRING),
                "home_side": openapi.Schema(type=openapi.TYPE_STRING),
                "away_side": openapi.Schema(type=openapi.TYPE_STRING),
                "match_day": openapi.Schema(type=openapi.TYPE_STRING),
                "match_time": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["stadium", "home_side", "away_side", "match_day", "match_time"],
        ),
        responses={
            201: "Match created successfully.",
            400: "Bad Request. Invalid request data.",
        },
    )
    def post(self, request: Request):
        """
        Create a new Match.

        :param request: The HTTP request object.
        :type request: Request
        :return: The HTTP response object.
        :rtype: Response
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        match = serializer.save()
        return self._create_response(
            data=self.serializer_class(match).data,
            status_code=status.HTTP_201_CREATED,
        )


class AddMatchSeatsView(BaseMatchView):
    """
    View for adding seats to a Match.

    # Request Body
    - `seats`: List of seat data.

    # Responses
    - 201 Created: Seats created successfully.
    - 400 Bad Request: Invalid request data or match not found.
    """

    serializer_class = SeatSerializer
    model_class = Match

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "seats": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                )
            },
        ),
        responses={
            201: "Seats created successfully.",
            400: "Bad Request. Invalid request data or match not found.",
        },
    )
    def post(self, request: Request, match_id: int):
        """
        Add seats to a Match.

        :param request: The HTTP request object.
        :type request: Request
        :param match_id: The ID of the Match.
        :type match_id: int
        :return: The HTTP response object.
        :rtype: Response
        """
        match, response = self._get_object_or_404(pk=match_id, error="Match not found")
        if response:
            return response

        seats_data: list[dict[str, int]] = request.data.get("seats", [])
        for seat_data in seats_data:
            seat_data["match"] = match.id

        serializer = self.serializer_class(
            data=seats_data, many=True, context={"match": match}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self._create_response(
            data={"message": "Seats created successfully"},
            status_code=status.HTTP_201_CREATED,
        )
