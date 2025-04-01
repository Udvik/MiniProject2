from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
import os
from datetime import datetime
from bson.objectid import ObjectId  # Fix _id issue in MongoDB queries

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["entertainment_recommendation"]
users_collection = db["users"]
friends_collection = db["friends"]
friend_requests_collection = db["friend_requests"]
recommendations_collection = db["recommendations"]

# 🟢 User Authentication
def register_user(username, password, preferences):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    if users_collection.find_one({"username": username}):
        return False  # Username already exists

    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "preferences": preferences,
        "watched": [],
        "liked": [],
        "friends": [],
        "friend_requests": []
    })
    return True

def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):  # ✅ Fix bcrypt check
        return {
            "username": user["username"],
            "preferences": user.get("preferences", [])
        }
    return None

def get_user_data(username):
    user = users_collection.find_one({"username": username})
    return {"preferences": user.get("preferences", [])} if user else {}

# 🟢 Watched & Liked Content Functions
def add_watched_content(username, media_type, item_id, title):
    if not username:
        return False  # Avoid updating without a valid user
    
    users_collection.update_one(
        {"username": username},
        {"$addToSet": {"watched": {
            "id": item_id,
            "type": media_type,
            "title": title,
            "added_at": datetime.utcnow().isoformat()  # Use UTC for consistency
        }}}
    )
    return True

def add_liked_content(username, media_type, item_id, title):
    if not username:
        return False
    
    users_collection.update_one(
        {"username": username},
        {"$addToSet": {"liked": {
            "id": item_id,
            "type": media_type,
            "title": title,
            "added_at": datetime.utcnow().isoformat()
        }}}
    )
    return True

def get_user_content(username):
    user = users_collection.find_one({"username": username})
    return {
        "watched": user.get("watched", []),  # ✅ Ensure empty list if no data
        "liked": user.get("liked", [])
    } if user else {"watched": [], "liked": []}

def remove_content(username, content_type, item_id):
    if not username:
        return False
    
    update_result = users_collection.update_one(
        {"username": username},
        {"$pull": {content_type: {"id": item_id}}}
    )
    return update_result.modified_count > 0

# 🟢 Friend System Functions
def send_friend_request(from_user, to_user):
    if from_user == to_user:
        return False
    
    existing_request = friend_requests_collection.find_one({
        "from_user": from_user,
        "to_user": to_user,
        "status": "pending"
    })

    if existing_request:
        return False  # Request already exists

    friend_requests_collection.insert_one({
        "from_user": from_user,
        "to_user": to_user,
        "status": "pending",
        "created_at": datetime.utcnow()
    })
    return True

def get_friend_requests(username):
    return list(friend_requests_collection.find({
        "$or": [
            {"to_user": username, "status": "pending"},
            {"from_user": username, "status": "pending"}
        ]
    }))

def respond_friend_request(request_id, action):
    try:
        request = friend_requests_collection.find_one({"_id": ObjectId(request_id)})  # ✅ Fix ObjectId issue
        if not request:
            return False

        if action == "accept":
            # Add to friends collection
            friends_collection.insert_one({
                "user1": request["from_user"],
                "user2": request["to_user"],
                "since": datetime.utcnow()
            })

            # Update both users' friends lists
            users_collection.update_one(
                {"username": request["from_user"]},
                {"$addToSet": {"friends": request["to_user"]}}
            )
            users_collection.update_one(
                {"username": request["to_user"]},
                {"$addToSet": {"friends": request["from_user"]}}
            )

        # Update request status
        friend_requests_collection.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "accepted" if action == "accept" else "rejected"}}
        )
        return True
    except Exception as e:
        print("Error:", e)
        return False

def get_friends(username):
    user = users_collection.find_one({"username": username})
    return user.get("friends", []) if user else []

# 🟢 Recommendation System Functions
def add_recommendation(from_user, to_user, media_type, item_id, title, note=""):
    recommendations_collection.insert_one({
        "from_user": from_user,
        "to_user": to_user,
        "media_type": media_type,
        "item_id": item_id,
        "title": title,
        "note": note,
        "created_at": datetime.utcnow(),
        "status": "active"
    })
    return True

def get_recommendations(username):
    return list(recommendations_collection.find({
        "to_user": username,
        "status": "active"
    }))

def remove_recommendation(recommendation_id):
    try:
        result = recommendations_collection.update_one(
            {"_id": ObjectId(recommendation_id)},  # ✅ Fix ObjectId issue
            {"$set": {"status": "removed"}}
        )
        return result.modified_count > 0
    except Exception as e:
        print("Error:", e)
        return False
