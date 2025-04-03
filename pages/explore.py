import streamlit as st
import os
import time
from models.recommendation_engine import RecommendationEngine
from db import get_user_content, get_friends
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
ITEMS_TO_SHOW = 16

# CSS Styling (keep your existing styles)

def fetch_tmdb_details(media_type, item_id):
    """Fetch details from TMDB API"""
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    response = requests.get(url, params={"api_key": TMDB_API_KEY})
    return response.json() if response.status_code == 200 else None

def get_user_watched_ids(username):
    """Get set of watched/liked items"""
    user_content = get_user_content(username)
    return {
        (item['type'], str(item['id']))
        for lst in [user_content.get('watched', []), user_content.get('liked', [])]
        for item in lst
    }

def display_recommendations(title, items, media_type):
    """Display items in grid"""
    st.markdown(f"## {title}")
    cols = st.columns(4)
    for idx, (item, _) in enumerate(items[:ITEMS_TO_SHOW]):
        with cols[idx % 4]:
            details = fetch_tmdb_details(item[0], item[1])
            if details:
                poster_path = details.get('poster_path')
                title = details.get('title') or details.get('name')
                poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None
                
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="/details?media_type={item[0]}&id={item[1]}" target="_blank">'
                    f'<img src="{poster_url or "https://via.placeholder.com/150x225?text=No+Poster"}" '
                    f'style="width:100%; border-radius:8px; aspect-ratio:2/3; object-fit:cover;">'
                    f'</a></div>',
                    unsafe_allow_html=True
                )
                st.caption(f"{title}")

# Main Page
def main():
    st.title("🎬 Explore Recommendations")
    
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in")
        return
    
    username = st.session_state["username"]
    exclude_ids = get_user_watched_ids(username)
    
    # Initialize engine
    engine = RecommendationEngine()
    engine.model_type = "neural"  # or "svd"
    
    # Get recommendations
    with st.spinner("Generating recommendations..."):
        movie_recs = engine.get_recommendations(username, "movie", exclude_ids, ITEMS_TO_SHOW)
        tv_recs = engine.get_recommendations(username, "tv", exclude_ids, ITEMS_TO_SHOW)
    
    # Display results
    display_recommendations("🎥 Recommended Movies", movie_recs, "movie")
    display_recommendations("📺 Recommended TV Shows", tv_recs, "tv")
    
    if st.button("← Back to Dashboard"):
        st.switch_page("pages/dashboard.py")

if __name__ == "__main__":
    main()