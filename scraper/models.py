from django.contrib.auth.models import User
from django.db import models

class Keyword(models.Model):
    keyword = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}'s Keyword: {self.keyword}"

class Link(models.Model):
    keyword = models.ForeignKey(Keyword,on_delete=models.CASCADE)
    url = models.URLField()
    title = models.CharField(max_length=200)
    total_ratings = models.IntegerField(default=0)
    rated = models.BooleanField(default=False)
    total_score = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)  # Field to store the average rating
    is_problem = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title} - {self.url}"

class MyLink(models.Model):
    keyword = models.ForeignKey(Keyword,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.ForeignKey(Link,on_delete=models.CASCADE)
    revisit = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    def __str__(self):
         return f"{self.user.username}"
