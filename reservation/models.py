from django.contrib.auth.models import User
from django.db import models


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey("matches.Match", on_delete=models.CASCADE)
    seat = models.ForeignKey("matches.Seat", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = "reservation"
        verbose_name_plural = "reservations"

    def __str__(self):
        return f"{self.user}:{self.match}:{self.seat}"
