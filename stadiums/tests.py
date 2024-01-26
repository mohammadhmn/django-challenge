from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from stadiums.models import Stadium


class AddStadiumView(APITestCase):
    def setUp(self):
        self.endpoint = "/api/stadiums/stadium/"

        self.super_user = User.objects.create_superuser(username="super_user")
        self.normal_user = User.objects.create_user(username="normal_user")

    def test_adding_new_stadium(self):
        self.client.force_authenticate(user=self.super_user)
        data = {
            "name": "new_stadium",
            "location": "somewhere",
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get("id"),
            Stadium.objects.get(name="new_stadium").id,
        )

    def test_adding_duplicate_stadium(self):
        self.client.force_authenticate(user=self.super_user)
        data = {
            "name": "new_stadium",
            "location": "somewhere",
        }
        Stadium.objects.create(**data)

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adding_new_stadium_without_name(self):
        self.client.force_authenticate(user=self.super_user)
        data = {
            "location": "somewhere",
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adding_new_stadium_without_location(self):
        self.client.force_authenticate(user=self.super_user)
        data = {
            "name": "new_stadium",
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adding_new_stadium_by_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        data = {
            "name": "new_stadium",
            "location": "somewhere",
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
