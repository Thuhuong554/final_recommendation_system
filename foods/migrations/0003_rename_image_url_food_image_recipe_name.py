# Generated by Django 5.1.1 on 2024-12-02 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0002_remove_food_recipe_remove_recipe_name_food_image_url_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='food',
            old_name='image_url',
            new_name='image',
        ),
        migrations.AddField(
            model_name='recipe',
            name='name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]