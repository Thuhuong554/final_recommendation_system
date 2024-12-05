from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=255)
    calories = models.IntegerField()
    image = models.URLField(max_length=500, blank=True, null=True)
    diet_type = models.CharField(
        max_length=50,
        choices=[
            ('vegan', 'Vegan'),
            ('keto', 'Keto'),
            ('low_carb', 'Low Carb'),
            ('eat_clean', 'Eat Clean'),
        ]
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='recipes')
    content = models.TextField()

    def __str__(self):
        return f"Recipe for {self.food.name}"
