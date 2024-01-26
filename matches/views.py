from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from matches.models import Match
from matches.serializers import MatchSerializer, SeatSerializer


class BaseMatchView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = None
    model_class = None

    def _get_object_or_404(self, pk: int, error: str):
        try:
            object = self.model_class.objects.get(pk=pk)
        except Match.DoesNotExist:
            return None, Response(
                {"error": error},
                status=status.HTTP_404_NOT_FOUND,
            )

        return object, None

    def _create_response(self, data: dict, status_code: int):
        return Response(data=data, status=status_code)


class AddMatchView(BaseMatchView):
    serializer_class = MatchSerializer
    model_class = Match

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        match = serializer.save()
        return self._create_response(
            data=self.serializer_class(match).data,
            status_code=status.HTTP_201_CREATED,
        )


class AddMatchSeatsView(BaseMatchView):
    serializer_class = SeatSerializer
    model_class = Match

    def post(self, request: Request, match_id: int):
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
