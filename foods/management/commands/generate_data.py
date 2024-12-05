import random
from django.core.management.base import BaseCommand
from faker import Faker
from foods.models import Food, Recipe

class Command(BaseCommand):
    help = 'Generate 1000+ realistic food and recipe records with images'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Clear existing data
        Food.objects.all().delete()
        Recipe.objects.all().delete()

        # Templates for realistic data
        food_templates = [
            {
                "name": "Grilled Chicken",
                "base_calories": 300,
                "diet_type": "eat_clean",
                "recipe": """Ingredients:
                - 2 boneless chicken breasts
                - 1 tsp olive oil
                - 1 tsp paprika
                - 1/2 tsp garlic powder
                - Salt and pepper to taste
                - 1 cup steamed broccoli (for serving)

                Instructions:
                1. Preheat the grill to medium-high heat.
                2. Rub the chicken breasts with olive oil, then season with paprika, garlic powder, salt, and pepper.
                3. Place the chicken on the grill and cook for 6-8 minutes on each side until fully cooked.
                4. Serve hot with steamed broccoli on the side.""",
                "image": "https://via.placeholder.com/150"
            },
            {
                "name": "Avocado Salad",
                "base_calories": 250,
                "diet_type": "vegan",
                "recipe": """Ingredients:
                - 1 ripe avocado
                - 1 cup baby spinach
                - 1/4 cup cherry tomatoes, halved
                - 1 tbsp lemon juice
                - Salt and pepper to taste

                Instructions:
                1. Slice the avocado into cubes and place them in a bowl.
                2. Add baby spinach and cherry tomatoes.
                3. Drizzle with lemon juice and season with salt and pepper.
                4. Toss gently to combine and serve immediately.""",
                "image": "https://via.placeholder.com/150"
            },
        ]

        foods = []
        recipes = []

        # Generate realistic data
        for _ in range(1000):
            template = random.choice(food_templates)
            food_name = f"{template['name']} ({fake.word().capitalize()})"
            calories = random.randint(
                max(50, template['base_calories'] - 50),
                template['base_calories'] + 50
            )
            diet_type = template['diet_type']
            image = template['image']

            # Create Food object
            food = Food(
                name=food_name,
                calories=calories,
                diet_type=diet_type,
                image=image
            )
            foods.append(food)

        # Bulk create Food objects
        Food.objects.bulk_create(foods)

        # Link recipes to created foods
        for food in Food.objects.all():
            template = random.choice(food_templates)
            recipe_content = f"{template['recipe']} Variation: {fake.sentence()}"
            recipe = Recipe(food=food, content=recipe_content)
            recipes.append(recipe)

        # Bulk create Recipe objects
        Recipe.objects.bulk_create(recipes)

        self.stdout.write(self.style.SUCCESS("Successfully created 1000+ realistic food and recipe records with images!"))
