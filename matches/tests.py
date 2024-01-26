from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from matches.models import Match, Seat
from stadiums.models import Stadium


class AddMatchViewTest(APITestCase):
    def setUp(self):
        self.endpoint = "/api/matches/match/"

        self.super_user = User.objects.create_superuser(username="super_user")
        self.normal_user = User.objects.create_user(username="normal_user")

        self.stadium_1 = Stadium.objects.create(
            name="stadium_1",
            location="some_city",
        )
        self.stadium_2 = Stadium.objects.create(
            name="stadium_2",
            location="some_city",
        )

    def test_add_new_match(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 2",
            "match_day": "2024-01-01",
            "match_time": "15:00:00",
            "stadium": self.stadium_1.id,
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get("id"),
            Match.objects.get(stadium=self.stadium_1).id,
        )

    def test_add_match_with_duplicate_home_side_and_datetime(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 2",
            "match_day": "2024-01-01",
            "match_time": "15:00:00",
            "stadium": self.stadium_1.id,
        }
        Match.objects.create(
            home_side=data["home_side"],
            away_side="Team 3",
            match_day=data["match_day"],
            match_time=data["match_time"],
            stadium=self.stadium_2,
        )

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_match_with_duplicate_away_side_and_datetime(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 2",
            "match_day": "2024-01-01",
            "match_time": "15:00:00",
            "stadium": self.stadium_1.id,
        }
        Match.objects.create(
            home_side="Team 3",
            away_side=data["home_side"],
            match_day=data["match_day"],
            match_time=data["match_time"],
            stadium=self.stadium_2,
        )

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_match_with_same_stadium_and_datetime(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 2",
            "match_day": "2024-01-01",
            "match_time": "15:00:00",
            "stadium": self.stadium_1.id,
        }
        Match.objects.create(
            home_side="Team 3",
            away_side="team_4",
            match_day=data["match_day"],
            match_time=data["match_time"],
            stadium=self.stadium_1,
        )

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_match_with_same_sides(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 1",
            "match_day": "2024-01-01",
            "match_time": "15:00:00",
            "stadium": self.stadium_1.id,
        }
        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_match_with_only_one_side(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "match_day": "2024-01-01",
            "match_time": "15:00:00",
            "stadium": self.stadium_1.id,
        }
        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_match_with_no_stadium(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 2",
            "match_day": "2024-01-01",
            "match_time": "15:00:00",
        }
        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_match_with_no_day(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 2",
            "match_time": "15:00:00",
            "stadium": self.stadium_1.id,
        }
        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_match_with_no_time(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 2",
            "match_day": "2024-01-01",
            "stadium": self.stadium_1.id,
        }
        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_match_as_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)

        data = {
            "home_side": "Team 1",
            "away_side": "Team 2",
            "match_day": "2024-01-01",
            "match_time": "15:00:00",
            "stadium": self.stadium_1.id,
        }

        response = self.client.post(path=self.endpoint, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AddMatchSeatsViewTest(APITestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(username="super_user")
        self.normal_user = User.objects.create_user(username="normal_user")

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
        self.endpoint = f"/api/matches/match/{self.match.id}/seats/"

    def test_add_seats_for_match(self):
        self.client.force_authenticate(user=self.super_user)

        data = {
            "seats": [
                {"seat_number": 1},
                {"seat_number": 2},
                {"seat_number": 3},
            ]
        }

        response = self.client.post(self.endpoint, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"), "Seats created successfully")
        self.assertEqual(
            Seat.objects.filter(match=self.match).count(), len(data["seats"])
        )

    def test_create_seats_for_invalid_match(self):
        self.client.force_authenticate(user=self.super_user)

        invalid_endpoint = (
            "/api/matches/match/100/seats/"  # Assuming 100 is an invalid match ID
        )

        data = {
            "seats": [
                {"seat_number": 1},
                {"seat_number": 2},
            ]
        }

        response = self.client.post(invalid_endpoint, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error"), "Match not found")

    def test_create_duplicate_seats(self):
        self.client.force_authenticate(user=self.super_user)

        Seat.objects.create(match=self.match, seat_number=1)
        data = {
            "seats": [
                {"seat_number": 1},
                {"seat_number": 2},
            ]
        }

        response = self.client.post(self.endpoint, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
