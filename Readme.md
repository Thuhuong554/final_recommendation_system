# TravelRec - Travel Destination Recommendation System

## Description
TravelRec is a Django-based web application that provides personalized travel destination recommendations. The system uses a hybrid recommendation approach combining collaborative filtering, content-based filtering, and bookmark-based recommendations to suggest travel destinations to users based on their preferences and interactions.

### Key Features
- User authentication and preference management
- Destination browsing with search and filtering capabilities
- Personalized destination recommendations
- User reviews and ratings
- Bookmark system for saving favorite destinations
- Detailed destination pages with similar destination suggestions
- Category-based organization of destinations

### Technical Features
- Hybrid recommendation system combining multiple approaches:
  - Collaborative filtering based on user ratings
  - Content-based filtering using destination keywords
  - Bookmark-based recommendations
- Django admin interface for content management
- Responsive UI using Tailwind CSS
- AJAX-powered bookmarking system
- Efficient database queries with proper indexing
- Data import system for bulk loading destinations and user interactions

## Installation and Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd travelrec
```

### Step 2: Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- Django
- scikit-learn
- numpy
- django-crispy-forms
- pillow
- python-dotenv

### Step 4: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 6: Load Initial Data
```bash
python manage.py import_data --destinations path/to/destinations.csv --interactions path/to/interactions.csv
python manage.py create_initial_categories
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to access the application.

## Data Format

### Destinations CSV Format
Required columns:
- Location name
- Location
- Describe
- Evaluate
- Image
- Keywords

Example:
```csv
Location name,Location,Describe,Evaluate,Image,Keywords
"Eiffel Tower","Paris, France","Iconic iron lattice tower...",4.5,http://example.com/eiffel.jpg,"['landmark', 'cultural', 'romantic']"
```

### User Interactions CSV Format
Required columns:
- User ID
- Destination Name
- Rating
- Review
- Interaction Timestamp

Example:
```csv
User ID,Destination Name,Rating,Review,Interaction Timestamp
user1,"Eiffel Tower",5,"Amazing experience!","2024-01-01 10:00:00"
```

## Project Structure
```
travelrec/
├── recommendations/
│   ├── management/
│   │   └── commands/
│   │       ├── import_data.py
│   │       └── create_initial_categories.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   ├── urls.py
│   └── recommender.py
├── templates/
│   ├── base.html
│   └── recommendations/
│       ├── home.html
│       ├── destination_list.html
│       └── destination_detail.html
└── static/
```

## Data Source and Inspiration
This project was inspired by the [Personalized Meal Recommendation System](https://github.com/sakshamhere/Personalized_meal_recommendation_system). While the original project focused on meal recommendations, we adapted its user interaction tracking and recommendation approaches for travel destinations.

The data format and collection methodology were influenced by the meal recommendation system's `recent_activity.csv`, but modified to suit travel-related content. Key adaptations include:
- Converting meal ratings to destination ratings
- Adapting food categories to travel categories
- Modifying the recommendation algorithm for travel-specific features
- Adding location-based similarities

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
