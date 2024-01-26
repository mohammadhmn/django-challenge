from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from matches.models import Match
from matches.serializers import MatchSerializer, SeatSerializer


class AddMatchView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = MatchSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        match = serializer.save()
        return Response(
            data=self.serializer_class(match).data,
            status=status.HTTP_201_CREATED,
        )


class AddMatchSeatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = SeatSerializer

    def post(self, request: Request, match_id: int):
        try:
            match = Match.objects.get(pk=match_id)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found"}, status=status.HTTP_404_NOT_FOUND
            )

        seats_data = request.data.get("seats", [])

        for seat_data in seats_data:
            seat_data["match"] = match.id

        serializer = self.serializer_class(
            data=seats_data, many=True, context={"match": match}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Seats created successfully"},
            status=status.HTTP_201_CREATED,
        )
