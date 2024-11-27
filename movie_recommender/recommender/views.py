from django.shortcuts import render
from .association_rule import generate_association_rules
# Create your views here.

def home(request):
    return render(request, "home.html")


def recommend_movies(request):
    rules = generate_association_rules()

    # Check the structure of the rules DataFrame
    print(rules.columns)  # This will help you confirm the column names

    recommendations = []
    for _, rule in rules.iterrows():
        recommendations.append({
            "antecedents": rule["antecedents"],  # If these are already strings, no need for list()
            "consequents": rule["consequents"],
            "lift": rule["lift"]
        })

    return render(request, "recommender/recommendations.html", {"recommendations": recommendations})

