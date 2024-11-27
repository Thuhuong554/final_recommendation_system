import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from .models import Movie, Rating

def generate_association_rules():
    # Step 1: Retrieve all ratings
    ratings = Rating.objects.all()
    data = {
        "user": [r.user.username for r in ratings],
        "movie": [r.movie.title for r in ratings],
        "rating": [r.rating for r in ratings],
    }
    df = pd.DataFrame(data)

    # Step 2: Prepare the data for association rule mining
    # Convert ratings to binary values (e.g., 0 if rating < 4, 1 if rating >= 4)
    df['rating'] = df['rating'].apply(lambda x: 1 if x >= 4 else 0)

    # Pivot the dataframe to create a user-movie matrix
    user_movie_matrix = df.pivot_table(index="user", columns="movie", values="rating", fill_value=0)

    # Step 3: Apply the Apriori algorithm
    frequent_itemsets = apriori(user_movie_matrix, min_support=0.1, use_colnames=True)

    # Step 4: Generate association rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1, num_itemsets=2)  # Specify num_itemsets

    return rules
