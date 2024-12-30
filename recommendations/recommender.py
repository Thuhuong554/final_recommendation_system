import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import Destination, UserInteraction
from django.db.models import Count, Avg, Q

class RecommendationEngine:
    def __init__(self):
        self.min_interactions = 5

    def get_user_item_matrix(self):
        interactions = UserInteraction.objects.filter(
            interaction_type='review'
        ).values('user_id', 'destination_id', 'rating')
        
        user_ids = list(set(i['user_id'] for i in interactions))
        dest_ids = list(set(i['destination_id'] for i in interactions))
        
        if not user_ids or not dest_ids:
            return np.array([]), [], []
        
        # Create user-item matrix
        matrix = np.zeros((len(user_ids), len(dest_ids)))
        user_idx = {id: idx for idx, id in enumerate(user_ids)}
        dest_idx = {id: idx for idx, id in enumerate(dest_ids)}
        
        for interaction in interactions:
            user_i = user_idx[interaction['user_id']]
            dest_i = dest_idx[interaction['destination_id']]
            matrix[user_i, dest_i] = interaction['rating']
        
        return matrix, user_ids, dest_ids

    def collaborative_filtering(self, user_id):
        matrix, user_ids, dest_ids = self.get_user_item_matrix()
        
        if matrix.size == 0 or user_id not in user_ids:
            return []
        
        user_idx = user_ids.index(user_id)
        user_similarities = cosine_similarity([matrix[user_idx]], matrix)[0]
        
        similar_users = [(i, sim) for i, sim in enumerate(user_similarities) if sim > 0 and i != user_idx]
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        user_ratings = matrix[user_idx]
        unrated_items = [i for i, rating in enumerate(user_ratings) if rating == 0]
        
        for item_idx in unrated_items:
            weighted_sum = 0
            sim_sum = 0
            for similar_user_idx, similarity in similar_users[:5]:
                if matrix[similar_user_idx][item_idx] > 0:
                    weighted_sum += similarity * matrix[similar_user_idx][item_idx]
                    sim_sum += similarity
            
            if sim_sum > 0:
                predicted_rating = weighted_sum / sim_sum
                recommendations.append({
                    'destination_id': dest_ids[item_idx],
                    'score': predicted_rating
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)

    def content_based_filtering(self, user_id):
        user_interactions = UserInteraction.objects.filter(
            user_id=user_id,
            interaction_type='review'
        ).select_related('destination')
        
        if not user_interactions:
            return []
        
        all_destinations = Destination.objects.all()
        recommendations = []
        
        for dest in all_destinations:
            if not any(ui.destination_id == dest.id for ui in user_interactions):
                score = 0
                for ui in user_interactions:
                    # Calculate similarity based on keywords with safety checks
                    dest_keywords = set(dest.keywords or [])
                    ui_dest_keywords = set(ui.destination.keywords or [])
                    
                    if dest_keywords and ui_dest_keywords:
                        common_keywords = dest_keywords & ui_dest_keywords
                        total_keywords = dest_keywords | ui_dest_keywords
                        if total_keywords:
                            keyword_similarity = len(common_keywords) / len(total_keywords)
                            score += keyword_similarity * ui.rating
                
                if score > 0:
                    recommendations.append({
                        'destination_id': dest.id,
                        'score': score / len(user_interactions)
                    })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)

    def get_bookmark_based_recommendations(self, user_id):
        """Generate recommendations based on user's bookmarked destinations"""
        # Get user's bookmarks
        bookmarked = UserInteraction.objects.filter(
            user_id=user_id,
            interaction_type='bookmark'
        ).select_related('destination')
        
        if not bookmarked:
            return []
        
        recommendations = []
        seen_destinations = set(b.destination_id for b in bookmarked)
        
        for bookmark in bookmarked:
            # Find similar destinations based on:
            # 1. Shared categories
            # 2. Similar rating
            # 3. Similar location
            similar_destinations = Destination.objects.filter(
                Q(categories__in=bookmark.destination.categories.all()) |
                Q(rating__range=(bookmark.destination.rating - 0.5, bookmark.destination.rating + 0.5)) |
                Q(location__icontains=bookmark.destination.location.split(',')[0])  # Compare city/region
            ).exclude(
                id__in=seen_destinations
            ).distinct()
            
            for dest in similar_destinations:
                # Calculate similarity score
                category_overlap = len(
                    set(dest.categories.all()) & 
                    set(bookmark.destination.categories.all())
                )
                rating_similarity = 1 - abs(dest.rating - bookmark.destination.rating) / 5
                location_similarity = 1.0 if dest.location.split(',')[0] == bookmark.destination.location.split(',')[0] else 0.0
                
                # Weighted similarity score
                similarity_score = (
                    0.5 * category_overlap +
                    0.3 * rating_similarity +
                    0.2 * location_similarity
                )
                
                recommendations.append({
                    'destination_id': dest.id,
                    'score': similarity_score
                })
        
        # Remove duplicates and sort by score
        unique_recommendations = {}
        for rec in recommendations:
            dest_id = rec['destination_id']
            if dest_id not in unique_recommendations or rec['score'] > unique_recommendations[dest_id]['score']:
                unique_recommendations[dest_id] = rec
        
        return sorted(unique_recommendations.values(), key=lambda x: x['score'], reverse=True)

    def get_hybrid_recommendations(self, user_id):
        """Enhanced hybrid recommendations including bookmark-based suggestions"""
        collab_recs = self.collaborative_filtering(user_id)
        content_recs = self.content_based_filtering(user_id)
        bookmark_recs = self.get_bookmark_based_recommendations(user_id)
        
        if not any([collab_recs, content_recs, bookmark_recs]):
            return []
        
        # Combine and normalize scores
        all_recs = {}
        
        # Add collaborative filtering scores
        for rec in collab_recs:
            all_recs[rec['destination_id']] = {'collab_score': rec['score']}
        
        # Add content-based scores
        for rec in content_recs:
            if rec['destination_id'] in all_recs:
                all_recs[rec['destination_id']]['content_score'] = rec['score']
            else:
                all_recs[rec['destination_id']] = {'content_score': rec['score']}
        
        # Add bookmark-based scores
        for rec in bookmark_recs:
            if rec['destination_id'] in all_recs:
                all_recs[rec['destination_id']]['bookmark_score'] = rec['score']
            else:
                all_recs[rec['destination_id']] = {'bookmark_score': rec['score']}
        
        # Calculate hybrid score (weighted average)
        recommendations = []
        for dest_id, scores in all_recs.items():
            collab_score = scores.get('collab_score', 0)
            content_score = scores.get('content_score', 0)
            bookmark_score = scores.get('bookmark_score', 0)
            
            # Weighted combination of all scores
            hybrid_score = (
                0.4 * collab_score +
                0.3 * content_score +
                0.3 * bookmark_score
            )
            
            recommendations.append({
                'destination_id': dest_id,
                'score': hybrid_score
            })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)