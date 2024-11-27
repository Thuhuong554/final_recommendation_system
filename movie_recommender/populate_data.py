import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommender.settings')

# Initialize Django
django.setup()

from recommender.models import Movie, User, Rating

def populate_data():
    # Create some users
    user1 = User.objects.create(username="user1", email="user1@example.com")
    user2 = User.objects.create(username="user2", email="user2@example.com")

    # Create some movies
    movie1 = Movie.objects.create(title="Movie 1", genre="Action", release_date="2020-01-01")
    movie2 = Movie.objects.create(title="Movie 2", genre="Comedy", release_date="2021-01-01")

    # Create some ratings
    Rating.objects.create(user=user1, movie=movie1, rating=5)
    Rating.objects.create(user=user1, movie=movie2, rating=3)
    Rating.objects.create(user=user2, movie=movie1, rating=4)

if __name__ == "__main__":
    populate_data()
