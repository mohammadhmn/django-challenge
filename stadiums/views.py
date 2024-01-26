from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from stadiums.serializers import StadiumSerializer


class AddStadiumView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = StadiumSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        stadium = serializer.save()
        return Response(
            data=self.serializer_class(stadium).data,
            status=status.HTTP_201_CREATED,
        )
