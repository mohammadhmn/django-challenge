from django.db import models


class Match(models.Model):
    stadium = models.ForeignKey("stadiums.Stadium", on_delete=models.PROTECT)
    home_side = models.CharField(max_length=50)
    away_side = models.CharField(max_length=50)
    match_day = models.DateField(auto_now=False, auto_now_add=False)
    match_time = models.TimeField(auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name = "match"
        verbose_name_plural = "matches"
        unique_together = ["stadium", "match_day", "match_time"]

    def __str__(self):
        return (
            f"{self.home_side} vs {self.away_side} on {self.datetime} at {self.stadium}"
        )


class Seat(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    is_reserved = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name = "seat"
        verbose_name_plural = "seats"
        unique_together = ["match", "seat_number"]

    def __str__(self):
        return f"{self.match.id}:{self.seat_number}"
