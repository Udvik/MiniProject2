from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
load_dotenv()
import os #Checking Changes 2

MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)

# Select database & collection
db = client["entertainment_recommendation"]
users_collection = db["users"]

# Register User
def register_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Check if user already exists
    if users_collection.find_one({"username": username}):
        return False  # Username taken

    # Insert new user
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

# Login User
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return True
    return False
