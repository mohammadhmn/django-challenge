from django.urls import path

from stadiums.views import AddStadiumView

urlpatterns = [
    path("stadium/", AddStadiumView.as_view(), name="add-stadium"),
]
