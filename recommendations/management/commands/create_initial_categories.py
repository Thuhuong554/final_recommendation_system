from django.core.management.base import BaseCommand
from recommendations.models import Category, Destination

class Command(BaseCommand):
    help = 'Creates initial categories from destination keywords'

    def handle(self, *args, **kwargs):
        # Get all unique keywords from destinations
        all_keywords = set()
        for dest in Destination.objects.all():
            if isinstance(dest.keywords, list):
                all_keywords.update(dest.keywords)
        
        # Create categories from keywords
        categories_created = 0
        for keyword in all_keywords:
            category, created = Category.objects.get_or_create(
                name=keyword.title(),
                defaults={'description': f'Destinations related to {keyword}'}
            )
            if created:
                categories_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {keyword}'))
        
        # Associate destinations with categories based on keywords
        for dest in Destination.objects.all():
            if isinstance(dest.keywords, list):
                for keyword in dest.keywords:
                    category = Category.objects.get(name=keyword.title())
                    dest.categories.add(category)
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {categories_created} categories and associated them with destinations'
        ))