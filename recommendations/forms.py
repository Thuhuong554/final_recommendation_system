# forms.py
from django import forms
from .models import UserInteraction, UserPreferences

class ReviewForm(forms.ModelForm):
    class Meta:
        model = UserInteraction
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'review': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
        }

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['favorite_categories']
        widgets = {
            'favorite_categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600'
            })
        }
