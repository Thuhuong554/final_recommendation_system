from django.contrib import admin
from .models import Category, Destination, UserInteraction, UserPreferences

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'rating', 'created_at')
    list_filter = ('categories', 'location')
    search_fields = ('name', 'location', 'description')
    filter_horizontal = ('categories',)

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'interaction_type', 'rating', 'interaction_timestamp')
    list_filter = ('interaction_type', 'interaction_timestamp')
    search_fields = ('user__username', 'destination__name')

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    filter_horizontal = ('favorite_categories',)
    search_fields = ('user__username',)