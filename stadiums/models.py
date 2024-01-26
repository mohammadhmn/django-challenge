from django.db import models


class Stadium(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)

    class Meta:
        verbose_name = "stadium"
        verbose_name_plural = "stadiums"
        unique_together = ["name", "location"]

    def __str__(self):
        return self.name
