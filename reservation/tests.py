from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from matches.models import Match, Seat
from stadiums.models import Stadium


class ReserveSeatViewTest(APITestCase):
    def setUp(self):
        self.endpoint = "/api/reservation/reserve/"

        self.user_1 = User.objects.create_user(username="user_1")
        self.user_2 = User.objects.create_user(username="user_2")
        self.stadium = Stadium.objects.create(
            name="some_stadium",
            location="some_city",
        )
        self.match = Match.objects.create(
            stadium=self.stadium,
            home_side="Team 1",
            away_side="Team 2",
            match_day="2024-01-01",
            match_time="15:00:00",
        )
        self.unreserved_seat = Seat.objects.create(
            match=self.match,
            seat_number=1,
            is_reserved=False,
        )
        self.reserved_seat = Seat.objects.create(
            match=self.match,
            seat_number=2,
            is_reserved=True,
        )

    def test_successful_reservation(self):
        self.client.force_authenticate(user=self.user_1)

        data = {
            "seat": self.unreserved_seat.id,
            "match": self.match.id,
        }

        response = self.client.post(self.endpoint, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"), "Successfully reserved the seat")
        self.assertEqual(Seat.objects.get(id=self.unreserved_seat.id).is_reserved, True)

    def test_seat_already_reserved(self):
        self.client.force_authenticate(user=self.user_1)

        data = {
            "seat": self.reserved_seat.id,
            "match": self.match.id,
        }

        response = self.client.post(self.endpoint, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("error"),
            "Seat is reserved or not available",
        )

    def test_seat_not_found(self):
        self.client.force_authenticate(user=self.user_1)

        data = {
            "seat": 100,
            "match": self.match.id,
        }

        response = self.client.post(self.endpoint, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("error"),
            "Seat is reserved or not available",
        )

    def test_match_not_found(self):
        self.client.force_authenticate(user=self.user_1)

        data = {
            "seat": self.unreserved_seat.id,
            "match": 100,
        }

        response = self.client.post(self.endpoint, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("error"),
            "Match not found",
        )

    def test_concurrent_update(self):
        client1 = APIClient()
        client1.force_authenticate(user=self.user_1)

        client2 = APIClient()
        client2.force_authenticate(user=self.user_2)

        data = {"match": self.match.id, "seat": self.unreserved_seat.id}

        response1 = client1.post(self.endpoint, data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = client2.post(self.endpoint, data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seat.objects.get(id=self.unreserved_seat.id).is_reserved, True)
