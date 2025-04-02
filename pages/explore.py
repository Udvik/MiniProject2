import streamlit as st
import requests
import os
from dotenv import load_dotenv
from collections import Counter
from db import get_user_content, get_friends, get_recommendations

# Load environment variables
load_dotenv()

# Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
ITEMS_PER_PAGE = 16

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
</style>
""", unsafe_allow_html=True)

# Authentication Check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access personalized recommendations")
    st.stop()

# Get username from session
username = st.session_state.get("username", "Guest")

# --- Helper Functions ---

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
    except Exception as e:
        st.error(f"Error fetching genres: {str(e)}")
        return {"movie": {}, "tv": {}}

def get_content_genres(media_type, item_id):
    """Get genres for a specific movie/TV show from TMDB"""
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
        response = requests.get(url, params={"api_key": TMDB_API_KEY}, timeout=10)
        if response.status_code == 200:
            return response.json().get("genres", [])
        return []
    except Exception:
        return []

def analyze_user_preferences(username):
    """Analyze user's preferences based on their activity"""
    user_content = get_user_content(username)
    friends = get_friends(username)
    recommendations = get_recommendations(username)
    
    genre_weights = Counter()
    
    # 1. User's liked content (highest weight)
    for item in user_content.get("liked", []):
        genres = get_content_genres(item["type"], item["id"])
        for genre in genres:
            genre_weights[genre["name"]] += 4
    
    # 2. Friends' recommendations (medium weight)
    for rec in recommendations:
        genres = get_content_genres(rec["media_type"], rec["item_id"])
        for genre in genres:
            genre_weights[genre["name"]] += 3
    
    # 3. User's watched content (lower weight)
    for item in user_content.get("watched", []):
        genres = get_content_genres(item["type"], item["id"])
        for genre in genres:
            genre_weights[genre["name"]] += 2
    
    # 4. Friends' liked content (lowest weight)
    for friend in friends:
        friend_content = get_user_content(friend)
        for item in friend_content.get("liked", []):
            genres = get_content_genres(item["type"], item["id"])
            for genre in genres:
                genre_weights[genre["name"]] += 1
    
    return genre_weights

def fetch_popular_content(media_type, limit=32):
    """Fetch popular content from TMDB"""
    try:
        url = f"https://api.themoviedb.org/3/trending/{media_type}/week"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "page": 1
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return [item for item in results if not item.get("adult", False)][:limit]
        return []
    except Exception:
        return []

def fetch_recommendations_by_genres(genres, media_type, limit=32):
    """Fetch recommendations based on genre preferences"""
    if not genres:
        return fetch_popular_content(media_type, limit)
    
    genre_mapping = fetch_tmdb_genres()
    genre_ids = []
    
    for genre_name in genres:
        for genre_id, name in genre_mapping[media_type].items():
            if name.lower() == genre_name.lower():
                genre_ids.append(str(genre_id))
                break
    
    if not genre_ids:
        return fetch_popular_content(media_type, limit)
    
    try:
        url = f"https://api.themoviedb.org/3/discover/{media_type}"
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": ",".join(genre_ids),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 100,
            "language": "en-US",
            "page": 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return [item for item in results if not item.get("adult", False)][:limit]
        return []
    except Exception:
        return []

def display_recommendation_section(title, recommendations, media_type):
    """Display a section of recommendations"""
    st.markdown(f"## {title}")
    
    if not recommendations:
        st.info(f"No recommendations available for {media_type}.")
        return
    
    if f"show_all_{media_type}" not in st.session_state:
        st.session_state[f"show_all_{media_type}"] = False
    
    show_all = st.session_state[f"show_all_{media_type}"]
    items_to_show = recommendations if show_all else recommendations[:ITEMS_PER_PAGE]
    
    cols = st.columns(4)
    for idx, item in enumerate(items_to_show):
        with cols[idx % 4]:
            poster_path = item.get("poster_path")
            title = item.get("title") or item.get("name")
            item_id = item.get("id")
            
            if poster_path and title and item_id:
                details_url = f"/details?media_type={media_type}&id={item_id}"
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{TMDB_IMAGE_BASE_URL}{poster_path}" width="150" style="border-radius:8px;margin-bottom:8px;">'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.caption(f"{title} ⭐ {item.get('vote_average', 'N/A')}")
    
    if len(recommendations) > ITEMS_PER_PAGE:
        if st.button(f"Show more {media_type}" if not show_all else "Show less",
                    key=f"toggle_{media_type}"):
            st.session_state[f"show_all_{media_type}"] = not st.session_state[f"show_all_{media_type}"]
            st.rerun()

# --- Main Page ---

st.title("🎬 Explore Recommendations")

with st.spinner("Analyzing your preferences..."):
    genre_preferences = analyze_user_preferences(username)
    
    # Get top 3 genres for each media type
    top_movie_genres = dict(sorted(genre_preferences.items(), key=lambda x: x[1], reverse=True)[:3])
    top_tv_genres = dict(sorted(genre_preferences.items(), key=lambda x: x[1], reverse=True)[:3])
    
    movie_recs = fetch_recommendations_by_genres(top_movie_genres, "movie")
    tv_recs = fetch_recommendations_by_genres(top_tv_genres, "tv")
    
    # Fallback to popular if no recommendations
    if not movie_recs:
        movie_recs = fetch_popular_content("movie")
    if not tv_recs:
        tv_recs = fetch_popular_content("tv")

display_recommendation_section("🎥 Recommended Movies", movie_recs, "movie")
display_recommendation_section("📺 Recommended TV Shows", tv_recs, "tv")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")