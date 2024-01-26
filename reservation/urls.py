from django.urls import path

from reservation.views import ReserveSeatView

urlpatterns = [
    path("reserve/", ReserveSeatView.as_view(), name="reserve-seat"),
]
