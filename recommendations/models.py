from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Destination(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    rating = models.FloatField(default=0.0)
    image_url = models.URLField()
    keywords = models.JSONField(default=list)
    categories = models.ManyToManyField(Category, related_name='destinations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recommendations:destination_detail', args=[str(self.id)])

    def update_rating(self):
        # Change from self.interactions to UserInteraction.objects
        avg_rating = UserInteraction.objects.filter(
            destination=self,
            interaction_type='review'
        ).aggregate(Avg('rating'))['rating__avg']
        self.rating = avg_rating if avg_rating else 0.0
        self.save()

class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey('Destination', on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20)  # 'view', 'review', 'bookmark'
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    interaction_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'destination', 'interaction_type']
        indexes = [
            models.Index(fields=['user', 'destination', 'interaction_type'])
        ]

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_categories = models.ManyToManyField(Category, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"
    
