from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class SignUpViewTest(APITestCase):
    def setUp(self) -> None:
        self.signup_endpoint = "/api/auth/signup/"

    def _test_signup(
        self, data: dict, expected_status: int, error_message: str = None
    ) -> Response:
        response = self.client.post(path=self.signup_endpoint, data=data)
        self.assertEqual(response.status_code, expected_status)
        if error_message:
            self.assertEqual(response.data.get("error"), error_message)
        return response

    def test_with_new_username(self) -> None:
        data = {"username": "newuser", "password": "newpassword"}
        response = self._test_signup(data, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data.get("token", None))
        self.assertIsNotNone(Token.objects.get(user__username=data["username"]))

    def test_with_existing_username(self) -> None:
        data = {"username": "testuser", "password": "testpassword"}
        User.objects.create_user(username=data["username"], password=data["password"])
        response = self._test_signup(
            data, status.HTTP_400_BAD_REQUEST, "Username already exists"
        )
        self.assertIsNone(response.data.get("token", None))

    def test_with_no_username(self) -> None:
        data = {"password": "testpassword"}
        response = self._test_signup(
            data, status.HTTP_400_BAD_REQUEST, "Username and password are required"
        )
        self.assertIsNone(response.data.get("token", None))

    def test_with_no_password(self) -> None:
        data = {"username": "testuser"}
        response = self._test_signup(
            data, status.HTTP_400_BAD_REQUEST, "Username and password are required"
        )
        self.assertIsNone(response.data.get("token", None))


class SignInViewTest(APITestCase):
    def setUp(self) -> None:
        self.signin_endpoint = "/api/auth/signin/"
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def _test_signin(self, data: dict, expected_status: int) -> None:
        response = self.client.post(path=self.signin_endpoint, data=data)
        self.assertEqual(response.status_code, expected_status)
        if expected_status == status.HTTP_200_OK:
            self.assertIsNotNone(response.data.get("token", None))
            self.assertEqual(
                Token.objects.get(user=self.user).key, response.data.get("token")
            )
        else:
            self.assertIsNone(response.data.get("token", None))

    def test_with_correct_credentials(self) -> None:
        data = {"username": self.username, "password": self.password}
        self._test_signin(data, status.HTTP_200_OK)

    def test_with_incorrect_username(self) -> None:
        data = {"username": "someusername", "password": self.password}
        self._test_signin(data, status.HTTP_400_BAD_REQUEST)

    def test_with_incorrect_password(self) -> None:
        data = {"username": self.username, "password": "somepassword"}
        self._test_signin(data, status.HTTP_400_BAD_REQUEST)
