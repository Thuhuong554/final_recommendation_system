# Generated by Django 5.1.1 on 2024-12-02 08:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0003_rename_image_url_food_image_recipe_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='name',
        ),
    ]
