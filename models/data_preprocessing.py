import pandas as pd
from datetime import datetime
from db import users_collection

class DataPreprocessor:
    @staticmethod
    def create_interaction_matrix():
        """Create user-item matrix from MongoDB"""
        data = []
        for user in users_collection.find():
            for list_type in ['watched', 'liked']:
                for item in user.get(list_type, []):
                    data.append({
                        'user': user['username'],
                        'item': f"{item['type']}_{item['id']}",
                        'rating': 1,
                        'timestamp': item.get('added_at', datetime.now())
                    })
        return pd.DataFrame(data)
    
    @staticmethod
    def get_item_features():
        """Extract features for content-based filtering"""
        features = {}
        # Implementation depends on your feature engineering needs
        return features