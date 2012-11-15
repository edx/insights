from django.db import models

# Create your models here.
class StudentBookAccesses(models.Model):
    username = models.CharField(max_length=500, unique=True) # TODO: Should not have max_length
    count = models.IntegerField()
