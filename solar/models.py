import datetime

from django.db import models

# Create your models here.
CHOICES_SOLAR = (
    (1, 'Solar 1'),
    (2, 'Solar 2'),
    (3, 'Solar 3'),
    (4, 'Solar 4'),
)


class Solar(models.Model):
    number_solar = models.IntegerField(choices=CHOICES_SOLAR)
    name = models.CharField(max_length=255)
    time = models.DateTimeField()
    value = models.FloatField()
    status = models.IntegerField()
    key = models.CharField(max_length=50, blank=True, null=True)
    crated_at = models.DateTimeField(auto_now_add=True)
    crated_at_new = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
