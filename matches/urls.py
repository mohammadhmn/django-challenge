from django.urls import path

from matches.views import AddMatchView, AddMatchSeatsView

urlpatterns = [
    path(
        "match/",
        AddMatchView.as_view(),
        name="add-match",
    ),
    path(
        "match/<int:match_id>/seats/",
        AddMatchSeatsView.as_view(),
        name="add-match-seats",
    ),
]
