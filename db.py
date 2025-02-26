# Updated db.py
from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client["entertainment_recommendation"]
users_collection = db["users"]

# Register User with Preferences
def register_user(username, password, preferences):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Check if user already exists
    if users_collection.find_one({"username": username}):
        return False  # Username taken

    # Insert new user with preferences
    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "preferences": preferences  # Store genre preferences
    })
    return True

# Login User
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return {"username": user["username"], "preferences": user.get("preferences", [])}  # Return user data including preferences
    return None
