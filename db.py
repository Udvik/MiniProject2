from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["entertainment_recommendation"]
users_collection = db["users"]

def register_user(username, password, preferences):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if users_collection.find_one({"username": username}):
        return False

    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "preferences": preferences,
        "watched": [],
        "liked": []
    })
    return True

def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return {
            "username": user["username"],
            "preferences": user.get("preferences", [])
        }
    return None

def get_user_data(username):
    user = users_collection.find_one({"username": username})
    if user:
        return {
            "email": user.get("email", "Not provided"),
            "join_date": str(user.get("join_date", "Unknown")),
            "preferences": user.get("preferences", [])
        }
    return {}

def add_watched_content(username, media_type, item_id, title):
    users_collection.update_one(
        {"username": username},
        {"$addToSet": {"watched": {"id": item_id, "type": media_type, "title": title}}},
        upsert=True
    )

def add_liked_content(username, media_type, item_id, title):
    users_collection.update_one(
        {"username": username},
        {"$addToSet": {"liked": {"id": item_id, "type": media_type, "title": title}}},
        upsert=True
    )

def get_user_content(username):
    user = users_collection.find_one({"username": username})
    return {
        "watched": user.get("watched", []),
        "liked": user.get("liked", [])
    }
def remove_content(username, content_type, item_id):
    """Remove item from watched or liked list"""
    update_result = users_collection.update_one(
        {"username": username},
        {"$pull": {content_type: {"id": item_id}}}
    )
    return update_result.modified_count > 0