from recommendation_engine import RecommendationEngine

if __name__ == "__main__":
    print("Training recommendation model...")
    engine = RecommendationEngine()
    engine.model_type = "neural"  # or "svd"
    engine.load_data()
    engine.train_model()
    engine.save_model()
    print("Model trained and saved successfully")