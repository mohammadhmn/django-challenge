from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
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
        username = request.data.get("username")
        password = request.data.get("password")
        return username, password

    def _error_response(self, message: str, status_code: int) -> Response:
        return Response(
            {"error": message},
            status=status_code,
        )

    def _username_exists(self, username: str) -> bool:
        return User.objects.filter(username=username).exists()

    def _create_user(self, username: str, password: str) -> User:
        return User.objects.create_user(username=username, password=password)

    def _get_or_create_token(self, user: User) -> Token:
        token, _ = Token.objects.get_or_create(user=user)
        return token
