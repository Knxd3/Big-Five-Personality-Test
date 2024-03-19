from django.db import models

# Create your models here.

class userScore(models.Model):
    user = models.CharField(max_length = 50)
    c = models.IntegerField()
    a = models.IntegerField()
    o = models.IntegerField()
    e = models.IntegerField()
    n = models.IntegerField()