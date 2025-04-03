import logging
from datetime import datetime

class RecommendationLogger:
    def __init__(self):
        logging.basicConfig(filename='rec_engine.log', level=logging.INFO)
        
    def log_prediction(self, user, items):
        logging.info(f"{datetime.now()} - User: {user}, Items: {items[:3]}...")