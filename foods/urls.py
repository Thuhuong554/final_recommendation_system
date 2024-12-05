from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('foods/', views.food_list, name='food_list'),
    path('recipes/', views.recipe_list, name='recipe_list'),  # URL for viewing all recipes
    path('recipes/<int:food_id>/', views.recipe_list, name='recipe_list_with_food'),  # URL for specific food recipes
    path('recommendation/', views.recommendation, name='recommendation')
]
