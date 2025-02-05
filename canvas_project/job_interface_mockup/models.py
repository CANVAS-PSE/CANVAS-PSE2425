from django.db import models
from django.utils import timezone


# Create your models here.
class Job(models.Model):
    starting_time = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE)
