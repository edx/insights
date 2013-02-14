from django.db import models
from datetime import datetime

class CronLock(models.Model):
    name = models.CharField(max_length=100)

    date_created = models.DateTimeField(auto_now_add = True)
    date_modified = models.DateTimeField(auto_now = True)

class CronJob(models.Model):
    name = models.CharField(max_length=100)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    time_between_runs = models.IntegerField(default=10) #in seconds
