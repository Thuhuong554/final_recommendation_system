from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Food, Recipe

# Homepage
def homepage(request):
    foods = Food.objects.all()
    return render(request, 'homepage.html', {'foods': foods})


# Food List View
def food_list(request):
    foods = Food.objects.all()  # Fetch all food records
    paginator = Paginator(foods, 6)  # 6 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'food_list.html', {'page_obj': page_obj})

# Recipe List View
def recipe_list(request, food_id=None):
    recipes = Recipe.objects.filter(food_id=food_id) if food_id else Recipe.objects.all()
    paginator = Paginator(recipes, 4)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'recipe_list.html', {'page_obj': page_obj})



# Helper function: Calculate calorie needs
def calculate_calorie_needs(weight, height, age, gender, activity_level):
    """Calculate daily calorie needs using the Mifflin-St Jeor Equation."""
    try:
        weight = float(weight)
        height = float(height)
        age = int(age)
    except ValueError:
        return 0  # Return 0 if inputs are invalid

    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # Female
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multiplier = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
    }

    return bmr * activity_multiplier.get(activity_level, 1.2)

# Recommendation View
def recommendation(request):
    recommendations = []
    calorie_needs = 0
    user_inputs = {
        'goal': request.GET.get('goal'),
        'gender': request.GET.get('gender'),
        'height': request.GET.get('height', 0),
        'weight': request.GET.get('weight', 0),
        'age': request.GET.get('age', 0),
        'activity': request.GET.get('activity'),
        'diet': request.GET.getlist('diet'),  # List of diets
    }

    try:
        # Ensure necessary inputs are valid and provided
        if user_inputs['gender'] and user_inputs['goal'] and user_inputs['activity']:
            calorie_needs = calculate_calorie_needs(
                user_inputs['weight'],
                user_inputs['height'],
                user_inputs['age'],
                user_inputs['gender'],
                user_inputs['activity']
            )

            if calorie_needs > 0:  # Valid calorie needs calculation
                # Adjust based on goal
                if user_inputs['goal'] == "gain":
                    calorie_needs += 500
                elif user_inputs['goal'] == "lose":
                    calorie_needs -= 500

                # Filter recommendations based on user diet preferences and calorie range
                query = Q(calories__lte=calorie_needs / 3)  # Single meal
                if user_inputs['diet']:
                    query &= Q(diet_type__in=user_inputs['diet'])

                recommendations = Food.objects.filter(query)[:6]
    except Exception as e:
        # Log or print the error if needed for debugging
        print(f"Error in recommendation calculation: {e}")

    return render(request, 'recommendation.html', {
        'user_inputs': user_inputs,
        'calorie_needs': round(calorie_needs) if calorie_needs else 0,
        'recommendations': recommendations,
    })
