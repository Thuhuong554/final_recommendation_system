import csv
import os
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from recommendations.models import Destination, UserInteraction, Category
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Import data from CSV files into the database"

    def add_arguments(self, parser):
        parser.add_argument('--destinations', type=str, help='csvfile/destination.csv')
        parser.add_argument('--interactions', type=str, help='csvfile/User_Interactions.csv')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['destinations']:
            self.import_destinations(options['destinations'])
        if options['interactions']:
            self.import_user_interactions(options['interactions'])

    def validate_csv_headers(self, fieldnames, required_headers, file_type):
        if not set(required_headers).issubset(fieldnames):
            missing = set(required_headers) - set(fieldnames)
            self.stderr.write(f"Missing headers in {file_type}: {missing}")
            return False
        return True

    def import_destinations(self, file_path):
        required_headers = {'Location name', 'Location', 'Describe', 'Evaluate', 'Image', 'Keywords'}
        
        if not os.path.exists(file_path):
            self.stderr.write(f"File not found: {file_path}")
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if not self.validate_csv_headers(reader.fieldnames, required_headers, 'destinations'):
                return

            for row in reader:
                try:
                    keywords = eval(row['Keywords']) if row['Keywords'] else []
                    rating = float(row['Evaluate'].split('/')[0]) if row['Evaluate'] else 0.0
                    image_url = row['Image'] if row['Image'].startswith('http') else ''

                    destination, created = Destination.objects.get_or_create(
                        name=row['Location name'],
                        defaults={
                            'location': row['Location'],
                            'description': row['Describe'],
                            'rating': rating,
                            'image_url': image_url,
                            'keywords': keywords
                        }
                    )
                    self.stdout.write(f"{'Created' if created else 'Updated'}: {destination.name}")
                except Exception as e:
                    self.stderr.write(f"Error processing {row.get('Location name', 'unknown')}: {str(e)}")

    def import_user_interactions(self, file_path):
        required_headers = {'User ID', 'Destination Name', 'Rating', 'Review', 'Interaction Timestamp'}
        
        if not os.path.exists(file_path):
            self.stderr.write(f"File not found: {file_path}")
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if not self.validate_csv_headers(reader.fieldnames, required_headers, 'interactions'):
                return

            for row in reader:
                try:
                    user, _ = User.objects.get_or_create(username=row['User ID'])
                    destination = Destination.objects.filter(name=row['Destination Name']).first()
                    
                    if not destination:
                        self.stderr.write(f"Destination not found: {row['Destination Name']}")
                        continue

                    interaction_type = 'review' if row.get('Review') else 'view'
                    timestamp = datetime.strptime(row['Interaction Timestamp'], "%Y-%m-%d %H:%M:%S")

                    interaction, created = UserInteraction.objects.get_or_create(
                        user=user,
                        destination=destination,
                        interaction_type=interaction_type,
                        defaults={
                            'rating': float(row['Rating']) if row.get('Rating') else None,
                            'review': row.get('Review'),
                            'interaction_timestamp': timestamp
                        }
                    )
                    self.stdout.write(f"{'Created' if created else 'Updated'} interaction: {user.username} - {destination.name}")
                except Exception as e:
                    self.stderr.write(f"Error processing interaction for {row.get('User ID', 'unknown')}: {str(e)}")