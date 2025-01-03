from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', LoginView.as_view(
        template_name='registration/login.html',
        redirect_field_name='next',
        next_page='recommendations:home'
    ), name='login'),
    path('accounts/logout/', LogoutView.as_view(
        next_page='recommendations:home',
        template_name='recommendations/home.html'
    ), name='logout'),
    path('destinations/', views.destination_list, name='destination_list'),
    path('destination/<int:destination_id>/', views.destination_detail, name='destination_detail'),
    path('destination/<int:destination_id>/review/', views.add_review, name='add_review'),
    path('destination/<int:destination_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('preferences/', views.update_preferences, name='update_preferences'),
    path('api/recommendations/', views.get_recommendations, name='get_recommendations'),
]