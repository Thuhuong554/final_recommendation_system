from django.contrib import messages
from django import forms
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Destination, UserInteraction, UserPreferences, Category
from .forms import ReviewForm, UserPreferencesForm
from .recommender import RecommendationEngine
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login


def home(request):
    """Home page with top-rated destinations and personalized recommendations"""
    top_destinations = Destination.objects.order_by('-rating')[:6]
    
    if request.user.is_authenticated:
        engine = RecommendationEngine()
        recommended_ids = [r['destination_id'] for r in 
                         engine.get_hybrid_recommendations(request.user.id)[:6]]
        recommended = Destination.objects.filter(id__in=recommended_ids)
    else:
        recommended = []

    return render(request, 'recommendations/home.html', {
        'top_destinations': top_destinations,
        'recommended_destinations': recommended
    })


def destination_list(request):
    """List all destinations with search and filter capabilities"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    destinations = Destination.objects.all()
    categories = Category.objects.all()
    
    if query:
        destinations = destinations.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category:
        destinations = destinations.filter(categories__name=category)
    
    # Add bookmark status for each destination
    if request.user.is_authenticated:
        bookmarked_destinations = set(UserInteraction.objects.filter(
            user=request.user,
            interaction_type='bookmark'
        ).values_list('destination_id', flat=True))
        
        for destination in destinations:
            destination.is_bookmarked = destination.id in bookmarked_destinations
    
    return render(request, 'recommendations/destination_list.html', {
        'destinations': destinations,
        'categories': categories,
        'query': query,
        'selected_category': category
    })

@login_required
def destination_detail(request, destination_id):
    """Detailed view of a destination with reviews and similar destinations"""
    destination = get_object_or_404(Destination, id=destination_id)
    
    # Record view interaction
    try:
        UserInteraction.objects.get_or_create(
            user=request.user,
            destination=destination,
            interaction_type='view',
            defaults={'rating': None, 'review': None}
        )
    except IntegrityError:
        pass
    
    # Get user's review if exists
    user_review = UserInteraction.objects.filter(
        user=request.user,
        destination=destination,
        interaction_type='review'
    ).first()
    
    # Get similar destinations with error handling
    try:
        engine = RecommendationEngine()
        similar_ids = [r['destination_id'] for r in 
                      engine.content_based_filtering(request.user.id)[:4]]
        similar_destinations = Destination.objects.filter(id__in=similar_ids)
        if not similar_destinations:
            similar_destinations = (Destination.objects.exclude(id=destination_id)
                                  .order_by('?')[:4])
    except Exception:
        similar_destinations = (Destination.objects.exclude(id=destination_id)
                              .order_by('?')[:4])
    
    # Get all reviews
    reviews = UserInteraction.objects.filter(
        destination=destination,
        interaction_type='review'
    ).select_related('user').order_by('-interaction_timestamp')
    
    # Check if destination is bookmarked
    is_bookmarked = UserInteraction.objects.filter(
        user=request.user,
        destination=destination,
        interaction_type='bookmark'
    ).exists()


    # Get bookmark count
    bookmark_count = UserInteraction.objects.filter(
        destination=destination,
        interaction_type='bookmark'
    ).count()
    
    # Get similar destinations based on bookmarks
    engine = RecommendationEngine()
    bookmark_based_recs = engine.get_bookmark_based_recommendations(request.user.id)
    similar_destinations = []
    
    if bookmark_based_recs:
        similar_ids = [r['destination_id'] for r in bookmark_based_recs[:4]]
        similar_destinations = Destination.objects.filter(id__in=similar_ids)
    
    if not similar_destinations:
        similar_destinations = (Destination.objects.exclude(id=destination_id)
                              .filter(categories__in=destination.categories.all())
                              .distinct()
                              .order_by('?')[:4])
    
    context = {
        'destination': destination,
        'bookmark_count': bookmark_count,
        'user_review': user_review,
        'reviews': reviews,
        'similar_destinations': similar_destinations,
        'is_bookmarked': is_bookmarked,
        'form': ReviewForm() if not user_review else ReviewForm(instance=user_review)
    }
    
    return render(request, 'recommendations/destination_detail.html', context)
@login_required
def add_review(request, destination_id):
    """Add or update a review for a destination"""
    destination = get_object_or_404(Destination, id=destination_id)
    
    # Get existing review if any
    review, created = UserInteraction.objects.get_or_create(
        user=request.user,
        destination=destination,
        interaction_type='review',
        defaults={'rating': None, 'review': None}
    )
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.interaction_type = 'review'
            review.save()
            
            # Update destination rating
            destination.update_rating()
            return redirect('recommendations:destination_detail', destination_id=destination_id)
    else:
        form = ReviewForm(instance=review if not created else None)
    
    return render(request, 'recommendations/review_form.html', {
        'form': form,
        'destination': destination
    })

@login_required
def toggle_bookmark(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    
    # Get or create bookmark interaction
    bookmark, created = UserInteraction.objects.get_or_create(
        user=request.user,
        destination=destination,
        interaction_type='bookmark',
        defaults={'rating': None, 'review': None}
    )
    
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_bookmarked': is_bookmarked
        })
    
    return redirect('recommendations:destination_detail', destination_id=destination_id)
    
@login_required
def update_preferences(request):
    """Update user preferences"""
    # Get or create preferences
    preferences, created = UserPreferences.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your preferences have been updated successfully!')
            return redirect('recommendations:home')
    else:
        form = UserPreferencesForm(instance=preferences)
    
    return render(request, 'recommendations/preferences_form.html', {
        'form': form,
        'categories': Category.objects.all()
    })
@login_required
def get_recommendations(request):
    """API endpoint for getting personalized recommendations"""
    try:
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        
        engine = RecommendationEngine()
        recommendations = engine.get_hybrid_recommendations(request.user.id)
        
        # Slice recommendations based on pagination
        paginated_recommendations = recommendations[offset:offset + limit]
        
        # Get full destination details
        destination_ids = [r['destination_id'] for r in paginated_recommendations]
        destinations = Destination.objects.filter(id__in=destination_ids)
        
        # Create response data
        response_data = []
        for rec in paginated_recommendations:
            destination = next(
                (d for d in destinations if d.id == rec['destination_id']), 
                None
            )
            if destination:
                response_data.append({
                    'id': destination.id,
                    'name': destination.name,
                    'location': destination.location,
                    'description': destination.description,
                    'rating': destination.rating,
                    'image_url': destination.image_url,
                    'recommendation_score': rec['score'],
                    'categories': list(destination.categories.values_list('name', flat=True))
                })
        
        return JsonResponse({
            'status': 'success',
            'count': len(recommendations),
            'next': offset + limit if offset + limit < len(recommendations) else None,
            'previous': offset - limit if offset > 0 else None,
            'results': response_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default preferences
            UserPreferences.objects.create(user=user)
            # Log the user in
            login(request, user)
            # Add success message
            messages.success(request, 'Registration successful! Please set your travel preferences.')
            return redirect('recommendations:update_preferences')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


class LoginView(LoginView):
    template_name = 'registration/login.html'