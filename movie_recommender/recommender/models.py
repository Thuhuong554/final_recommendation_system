from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    release_date = models.DateField()

    def __str__(self):
        return self.title

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()

    def __str__(self):
        return self.username

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def __str__(self):
        return f'{self.user} rated {self.movie} {self.rating}'
