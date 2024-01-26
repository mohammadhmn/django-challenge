from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class SignUpView(APIView):
    """
    View for user registration and account creation.

    ---
    # Request Body
    - `username`: The desired username for the new user.
    - `password`: The password for the new user.

    # Responses
    - 201 Created: The user account was successfully created. Returns a token.
    - 400 Bad Request: If the request is missing required fields or the username already exists.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["username", "password"],
        ),
        responses={
            201: "User account created successfully. Returns a token.",
            400: "Bad Request. If the request is missing required fields or the username already exists.",
        },
    )
    def post(self, request: Request) -> Response:
        """
        Create a new user account.

        :param request: The HTTP request object.
        :type request: Request
        :return: The HTTP response object.
        :rtype: Response
        """
        username, password = self._get_username_password(request)

        if not (username and password):
            return self._error_response(
                "Username and password are required", status.HTTP_400_BAD_REQUEST
            )

        if self._username_exists(username):
            return self._error_response(
                "Username already exists", status.HTTP_400_BAD_REQUEST
            )

        user = self._create_user(username, password)
        token = self._get_or_create_token(user)

        return Response(
            {"token": token.key},
            status=status.HTTP_201_CREATED,
        )

    def _get_username_password(self, request: Request) -> tuple[str, str]:
        """
        Extract username and password from the request data.

        :param request: The HTTP request object.
        :type request: Request
        :return: A tuple containing the username and password.
        :rtype: tuple[str, str]
        """
        username = request.data.get("username")
        password = request.data.get("password")
        return username, password

    def _error_response(self, message: str, status_code: int) -> Response:
        """
        Create an error response with the given message and status code.

        :param message: The error message.
        :type message: str
        :param status_code: The HTTP status code.
        :type status_code: int
        :return: The HTTP response object.
        :rtype: Response
        """
        return Response(
            {"error": message},
            status=status_code,
        )

    def _username_exists(self, username: str) -> bool:
        """
        Check if a user with the given username already exists.

        :param username: The username to check.
        :type username: str
        :return: True if the username exists, False otherwise.
        :rtype: bool
        """
        return User.objects.filter(username=username).exists()

    def _create_user(self, username: str, password: str) -> User:
        """
        Create a new user with the given username and password.

        :param username: The desired username.
        :type username: str
        :param password: The user's password.
        :type password: str
        :return: The created User object.
        :rtype: User
        """
        return User.objects.create_user(username=username, password=password)

    def _get_or_create_token(self, user: User) -> Token:
        """
        Get or create an authentication token for the given user.

        :param user: The user for whom to get or create a token.
        :type user: User
        :return: The authentication token.
        :rtype: Token
        """
        token, _ = Token.objects.get_or_create(user=user)
        return token
