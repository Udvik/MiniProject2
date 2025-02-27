# Updated db.py
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
        "preferences": preferences  
    })
    return True


def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return {"username": user["username"], "preferences": user.get("preferences", [])} 
    return None
