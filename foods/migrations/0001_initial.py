# Generated by Django 5.1.1 on 2024-12-02 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('calories', models.IntegerField()),
                ('recipe', models.TextField()),
                ('diet_type', models.CharField(choices=[('vegan', 'Vegan'), ('keto', 'Keto'), ('low_carb', 'Low Carb'), ('eat_clean', 'Eat Clean')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField()),
            ],
        ),
    ]