from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from stadiums.serializers import StadiumSerializer


class AddStadiumView(APIView):
    """
    View for adding a new stadium.

    ---
    # Permissions
    - User must be authenticated.
    - User must be an admin.

    # Request Body
    - `name`: The name of the stadium.
    - `location`: The location of the stadium.

    # Responses
    - 201 Created: Stadium created successfully.
    - 400 Bad Request: Invalid request data.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = StadiumSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "location": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["name", "location"],
        ),
        responses={
            201: "Stadium created successfully.",
            400: "Bad Request. Invalid request data.",
        },
    )
    def post(self, request: Request):
        """
        Create a new stadium.

        :param request: The HTTP request object.
        :type request: Request
        :return: The HTTP response object.
        :rtype: Response
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )
