import os
import pickle
import numpy as np
import pandas as pd
from surprise import Dataset, Reader, SVD
from tensorflow.keras.models import Model, save_model, load_model
from tensorflow.keras.layers import Input, Embedding, Flatten, Dot, Dense
from tensorflow.keras.optimizers import Adam
from collections import defaultdict
from db import users_collection
import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

class RecommendationEngine:
    def __init__(self):
        self.user_item_ratings = defaultdict(dict)
        self.item_features = {}
        self.user_ids = {}
        self.item_ids = {}
        self.model = None
        self.model_type = "neural"  # or "svd"
        
    def load_data(self):
        """Load and prepare data from MongoDB"""
        # Create mappings
        all_users = users_collection.distinct("username")
        self.user_ids = {u: i for i, u in enumerate(all_users)}
        
        # Build user-item matrix and collect all items
        all_items = set()
        for user in users_collection.find():
            for list_type in ['watched', 'liked']:
                for item in user.get(list_type, []):
                    key = (item['type'], str(item['id']))
                    self.user_item_ratings[user['username']][key] = 1
                    all_items.add(key)
        
        self.item_ids = {item: i for i, item in enumerate(all_items)}
        
    def train_model(self):
        """Train the selected model type"""
        if self.model_type == "svd":
            self._train_svd()
        else:
            self._train_neural()
    
    def _train_svd(self):
        """Train Surprise SVD model"""
        records = []
        for user, items in self.user_item_ratings.items():
            for item, rating in items.items():
                records.append([user, f"{item[0]}_{item[1]}", rating])
        
        df = pd.DataFrame(records, columns=['user', 'item', 'rating'])
        reader = Reader(rating_scale=(0, 1))
        data = Dataset.load_from_df(df, reader)
        trainset = data.build_full_trainset()
        
        self.model = SVD(n_factors=50, n_epochs=20)
        self.model.fit(trainset)
        
    def _train_neural(self):
        """Train neural collaborative filtering model"""
        # Prepare training data
        X_user, X_item, y = [], [], []
        for user, items in self.user_item_ratings.items():
            for item, rating in items.items():
                X_user.append(self.user_ids[user])
                X_item.append(self.item_ids[item])
                y.append(rating)
        
        # Model architecture
        user_input = Input(shape=(1,))
        item_input = Input(shape=(1,))
        
        user_embed = Embedding(len(self.user_ids), 64)(user_input)
        item_embed = Embedding(len(self.item_ids), 64)(item_input)
        
        dot_product = Dot(axes=2)([user_embed, item_embed])
        flattened = Flatten()(dot_product)
        output = Dense(1, activation='sigmoid')(flattened)
        
        self.model = Model(inputs=[user_input, item_input], outputs=output)
        self.model.compile(optimizer=Adam(0.001), loss='binary_crossentropy')
        
        # Train
        self.model.fit(
            [np.array(X_user), np.array(X_item)], 
            np.array(y),
            epochs=10,
            batch_size=64
        )
    
    def get_recommendations(self, username, media_type, exclude_ids, n=10):
        """Get personalized recommendations"""
        if not self.model:
            self.load_data()
            self.train_model()
        
        # Get all candidate items
        candidates = [
            item for item in self.item_ids.keys() 
            if item[0] == media_type and item not in exclude_ids
        ]
        
        if self.model_type == "svd":
            predictions = []
            for item in candidates:
                pred = self.model.predict(username, f"{item[0]}_{item[1]}")
                predictions.append((item, pred.est))
        else:
            # Neural network predictions
            user_idx = np.array([self.user_ids[username]] * len(candidates))
            item_idx = np.array([self.item_ids[item] for item in candidates])
            preds = self.model.predict([user_idx, item_idx]).flatten()
            predictions = list(zip(candidates, preds))
        
        # Sort and return top N
        return sorted(predictions, key=lambda x: x[1], reverse=True)[:n]
    
    def save_model(self, path="models/trained_models/"):
        """Save trained model"""
        os.makedirs(path, exist_ok=True)
        if self.model_type == "svd":
            with open(f"{path}svd_model.pkl", 'wb') as f:
                pickle.dump(self.model, f)
        else:
            self.model.save(f"{path}neural_model.h5")
    
    def load_saved_model(self):
        """Load pre-trained model"""
        model_path = "models/trained_models/"
        if self.model_type == "svd" and os.path.exists(f"{model_path}svd_model.pkl"):
            with open(f"{model_path}svd_model.pkl", 'rb') as f:
                self.model = pickle.load(f)
        elif os.path.exists(f"{model_path}neural_model.h5"):
            self.model = load_model(f"{model_path}neural_model.h5")