from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class SignUpViewTest(APITestCase):
    def setUp(self):
        self.endpoint = "/api/auth/signup/"

    def test_with_new_username(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data.get("token", None))
        self.assertIsNotNone(Token.objects.get(user__username=data["username"]))

    def test_with_existing_username(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
        }

        User.objects.create_user(username=data["username"], password=data["password"])

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data.get("token", None))
        self.assertEqual(
            response.data.get("error"),
            "Username already exists",
        )

    def test_with_no_username(self):
        data = {
            "password": "testpassword",
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data.get("token", None))
        self.assertEqual(
            response.data.get("error"),
            "Username and password are required",
        )

    def test_with_no_password(self):
        data = {
            "username": "testuser",
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data.get("token", None))
        self.assertEqual(
            response.data.get("error"),
            "Username and password are required",
        )


class ObtainAuthTokenViewTest(APITestCase):
    def setUp(self):
        self.endpoint = "/api/auth/signin/"

        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_with_correct_credentials(self):
        data = {
            "username": self.username,
            "password": self.password,
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("token", None))
        self.assertEqual(
            Token.objects.get(user=self.user).key,
            response.data.get("token"),
        )

    def test_with_incorrect_username(self):
        data = {
            "username": "someusername",
            "password": self.password,
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data.get("token", None))

    def test_with_incorrect_password(self):
        data = {
            "username": self.username,
            "password": "somepassword",
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data.get("token", None))
