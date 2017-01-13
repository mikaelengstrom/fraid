from django.db import models


# Create your models here.
class Sequence(models.Model):
    sequence = models.IntegerField()
    upcoming = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
