import streamlit as st
import requests
import os
import random
from dotenv import load_dotenv
from collections import Counter
from db import get_user_content, get_friends, get_recommendations
import hashlib
import time

# Load environment variables
load_dotenv()

# Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
ITEMS_TO_SHOW = 16

# Set page config
st.set_page_config(page_title="Explore Recommendations", layout="wide")

# CSS Styling
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > .main {
        padding: 2rem 5rem !important;
    }
    @media (max-width: 768px) {
        [data-testid="stAppViewContainer"] > .main {
            padding: 2rem 1rem !important;
        }
    }
    .poster-container {
        position: relative;
        margin-bottom: 8px;
    }
    .poster-container img {
        transition: transform 0.2s;
    }
    .poster-container img:hover {
        transform: scale(1.03);
        cursor: pointer;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Authentication Check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access personalized recommendations")
    st.stop()

# Get username from session
username = st.session_state.get("username", "Guest")

# --- Helper Functions ---

def get_content_fingerprint():
    """Create unique fingerprint that changes with login state and time"""
    user_content = get_user_content(username)
    friends = get_friends(username)
    recommendations = get_recommendations(username)
    return hashlib.sha256(
        f"{user_content}{friends}{recommendations}{time.time()}".encode()
    ).hexdigest()

def get_user_watched_ids():
    """Get set of all watched content IDs for the user"""
    user_content = get_user_content(username)
    return {(item["type"], item["id"]) for item in user_content.get("watched", [])}

def fetch_tmdb_genres():
    """Fetch genre mappings from TMDB API"""
    try:
        movie_genres = requests.get(
            "https://api.themoviedb.org/3/genre/movie/list",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        ).json().get("genres", [])
        
        tv_genres = requests.get(
            "https://api.themoviedb.org/3/genre/tv/list",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        ).json().get("genres", [])
        
        return {
            "movie": {g["id"]: g["name"] for g in movie_genres},
            "tv": {g["id"]: g["name"] for g in tv_genres}
        }
    except Exception:
        return {"movie": {}, "tv": {}}

def analyze_user_preferences():
    """Analyze user's preferences with randomization factor"""
    user_content = get_user_content(username)
    friends = get_friends(username)
    recommendations = get_recommendations(username)
    
    genre_weights = Counter()
    
    # 1. User's liked content (highest weight with randomness)
    for item in user_content.get("liked", []):
        try:
            url = f"https://api.themoviedb.org/3/{item['type']}/{item['id']}"
            response = requests.get(url, params={"api_key": TMDB_API_KEY}, timeout=5)
            if response.status_code == 200:
                for genre in response.json().get("genres", []):
                    genre_weights[genre["name"]] += 8 + random.random()
        except:
            continue
    
    # 2. Friends' recommendations (medium weight if matching with randomness)
    for rec in recommendations:
        try:
            url = f"https://api.themoviedb.org/3/{rec['media_type']}/{rec['item_id']}"
            response = requests.get(url, params={"api_key": TMDB_API_KEY}, timeout=5)
            if response.status_code == 200:
                for genre in response.json().get("genres", []):
                    if genre["name"] in genre_weights:
                        genre_weights[genre["name"]] += 4 + random.random()
        except:
            continue
    
    # If no preferences, use some default genres
    if not genre_weights:
        return {"Action": 5, "Comedy": 5, "Drama": 5}
    
    return genre_weights

def fetch_tmdb_recommendations(genres, media_type, exclude_ids):
    """Fetch recommendations with strong preference for popular/high-rated content"""
    genre_mapping = fetch_tmdb_genres()
    genre_ids = []
    
    # Convert genre names to IDs
    for genre_name in genres:
        for genre_id, name in genre_mapping[media_type].items():
            if name.lower() == genre_name.lower():
                genre_ids.append(str(genre_id))
                break
    
    try:
        # Add some randomness to parameters
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": ",".join(genre_ids),
            "sort_by": "popularity.desc,vote_average.desc",
            "vote_count.gte": 50,
            "vote_average.gte": 6.0,
            "language": "en-US",
            "page": random.randint(1, 3)  # Random page for variety
        }
        
        url = f"https://api.themoviedb.org/3/discover/{media_type}"
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            results = response.json().get("results", [])
            # Filter out watched and adult content
            filtered = [
                item for item in results 
                if not item.get("adult", False) and 
                (media_type, item["id"]) not in exclude_ids
            ]
            return filtered[:ITEMS_TO_SHOW]
    except Exception:
        pass
    
    # Fallback to trending content if discovery fails
    try:
        url = f"https://api.themoviedb.org/3/trending/{media_type}/week"
        params = {"api_key": TMDB_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            results = response.json().get("results", [])
            filtered = [
                item for item in results 
                if not item.get("adult", False) and 
                (media_type, item["id"]) not in exclude_ids
            ]
            return filtered[:ITEMS_TO_SHOW]
    except Exception:
        pass
    
    # Final fallback - return empty list if all fails
    return []

def display_recommendations(title, recommendations, media_type):
    """Display recommendations in a grid"""
    st.markdown(f"## {title}")
    
    if not recommendations:
        st.info(f"Loading {media_type} recommendations...")
        return
    
    cols = st.columns(4)
    for idx, item in enumerate(recommendations[:ITEMS_TO_SHOW]):
        with cols[idx % 4]:
            poster_path = item.get("poster_path")
            title = item.get("title") or item.get("name")
            item_id = item.get("id")
            
            if poster_path and title and item_id:
                poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else "https://via.placeholder.com/150x225?text=No+Poster"
                details_url = f"/details?media_type={media_type}&id={item_id}"
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{poster_url}" width="150" style="border-radius:8px;margin-bottom:8px;">'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                rating = item.get("vote_average", "N/A")
                st.caption(f"{title} ⭐ {rating}")

# --- Main Page ---

st.title("🎬 Explore Recommendations")

# Initialize session state
if "recommendations_data" not in st.session_state:
    st.session_state.recommendations_data = {
        "fingerprint": "",
        "movie_recs": [],
        "tv_recs": []
    }

# Check if we need to refresh
current_fingerprint = get_content_fingerprint()
if current_fingerprint != st.session_state.recommendations_data["fingerprint"]:
    with st.spinner("Updating recommendations..."):
        watched_ids = get_user_watched_ids()
        genre_weights = analyze_user_preferences()
        
        # Get top genres by weight
        top_genres = [g[0] for g in sorted(genre_weights.items(), key=lambda x: x[1], reverse=True)[:3]]
        
        # Fetch new recommendations
        st.session_state.recommendations_data = {
            "fingerprint": current_fingerprint,
            "movie_recs": fetch_tmdb_recommendations(top_genres, "movie", watched_ids) or [],
            "tv_recs": fetch_tmdb_recommendations(top_genres, "tv", watched_ids) or []
        }

# Refresh button
if st.button("🔄 Refresh Recommendations", key="refresh_btn"):
    st.session_state.recommendations_data["fingerprint"] = ""
    st.rerun()

# Display recommendations
display_recommendations("🎥 Recommended Movies", 
                       st.session_state.recommendations_data["movie_recs"], 
                       "movie")
display_recommendations("📺 Recommended TV Shows", 
                       st.session_state.recommendations_data["tv_recs"], 
                       "tv")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")