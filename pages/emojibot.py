import requests
import random
import streamlit as st
import os
from dotenv import load_dotenv
import emoji

# Load API Key from .env
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    st.error("API Key not found! Make sure to set it in the .env file.")
    st.stop()

# TMDB URLs
TMDB_GENRES_LIST_URL = "https://api.themoviedb.org/3/genre/movie/list"
TMDB_TV_GENRES_LIST_URL = "https://api.themoviedb.org/3/genre/tv/list"
TMDB_MOVIES_URL = "https://api.themoviedb.org/3/discover/movie"
TMDB_TV_URL = "https://api.themoviedb.org/3/discover/tv"
TMDB_TRENDING_URL = "https://api.themoviedb.org/3/trending/{media_type}/week"

# Updated Emoji-to-Genre Mapping with better TV show coverage
EMOJI_TO_GENRE = {
    # Happy/Comforting
    ("😀", "😊", "🤗"): {
        "movie": ["Comedy", "Adventure"],
        "tv": ["Comedy", "Animation"]
    },
    # Sad/Emotional
    ("😢", "😭"): {
        "movie": ["Drama", "Romance"],
        "tv": ["Drama", "Soap"]
    },
    # Angry
    ("😡", "🤬"): {
        "movie": ["Action", "Thriller"],
        "tv": ["Action & Adventure", "Crime"]
    },
    # Scary
    ("😱", "👻", "🎃"): {
        "movie": ["Horror", "Mystery"],
        "tv": ["Horror", "Mystery"]
    },
    # Mind-blown
    ("😮", "🤯"): {
        "movie": ["Sci-Fi", "Fantasy"],
        "tv": ["Sci-Fi & Fantasy", "Documentary"]
    },
    # Neutral/Informational
    ("😐", "📜", "🤓"): {
        "movie": ["Documentary", "History"],
        "tv": ["Documentary", "News"]
    },
    # Love
    ("❤️", "💔", "🥰"): {
        "movie": ["Romance", "Drama"],
        "tv": ["Romance", "Reality"]
    },
    # Musical
    ("🎶", "🎵"): {
        "movie": ["Music", "Musical"],
        "tv": ["Music", "Reality"]
    }
}

# Fetch TMDB Genre Mapping with caching
@st.cache_data
def fetch_genre_mapping():
    movie_response = requests.get(TMDB_GENRES_LIST_URL, params={"api_key": API_KEY})
    tv_response = requests.get(TMDB_TV_GENRES_LIST_URL, params={"api_key": API_KEY})
    
    mapping = {"movie": {}, "tv": {}}
    
    if movie_response.status_code == 200:
        for genre in movie_response.json().get("genres", []):
            mapping["movie"][genre["name"]] = genre["id"]
    
    if tv_response.status_code == 200:
        for genre in tv_response.json().get("genres", []):
            mapping["tv"][genre["name"]] = genre["id"]
    
    return mapping

GENRE_MAPPING = fetch_genre_mapping()

def fetch_content(genre_ids, content_type="movie", sort_by="popularity.desc"):
    try:
        url = TMDB_MOVIES_URL if content_type == "movie" else TMDB_TV_URL
        params = {
            "api_key": API_KEY,
            "with_genres": ",".join(map(str, genre_ids)),
            "sort_by": sort_by,
            "vote_count.gte": 100  # Ensure only reasonably popular content
        }
        response = requests.get(url, params=params, timeout=10)
        return response.json().get("results", []) if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []

def fetch_trending(content_type="movie"):
    try:
        url = TMDB_TRENDING_URL.format(media_type=content_type)
        params = {"api_key": API_KEY}
        response = requests.get(url, params=params, timeout=10)
        return response.json().get("results", []) if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []

# Streamlit UI
st.title("🎬 Emoji-Based Movie & TV Show Recommendation")

selected_emoji = st.selectbox(
    "Select your current mood:", 
    sorted(list(set(emoji for emojis in EMOJI_TO_GENRE.keys() for emoji in emojis)))
)

if selected_emoji:
    st.write(f"**Detected Emotion:** {emoji.demojize(selected_emoji).replace(':', '').capitalize()}")

    # Find genres for the selected emoji
    genres = next((v for k, v in EMOJI_TO_GENRE.items() if selected_emoji in k), None)
    
    if genres:
        # Get genre IDs for both movie and TV
        movie_genre_ids = [GENRE_MAPPING["movie"][g] for g in genres["movie"] if g in GENRE_MAPPING["movie"]]
        tv_genre_ids = [GENRE_MAPPING["tv"][g] for g in genres["tv"] if g in GENRE_MAPPING["tv"]]

        # First try to get content by genre, fall back to trending if no results
        movies = fetch_content(movie_genre_ids, "movie") or fetch_trending("movie")
        tv_shows = fetch_content(tv_genre_ids, "tv") or fetch_trending("tv")

        # Show Movies Section
        if movies:
            st.subheader("🎥 Recommended Movies")
            cols = st.columns(5)
            for idx, movie in enumerate(movies[:10]):  # Show top 10
                title = movie.get("title", "Unknown")
                poster_path = movie.get("poster_path", "")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/180x270"
                item_id = movie.get("id")
                
                with cols[idx % 5]:
                    details_url = f"/details?media_type=movie&id={item_id}"
                    st.markdown(f"[![{title}]({poster_url})]({details_url})", unsafe_allow_html=True)
                    st.write(title)
        else:
            st.write("❌ No movie recommendations found for this mood.")

        # Show TV Shows Section
        if tv_shows:
            st.subheader("📺 Recommended TV Shows")
            cols = st.columns(5)
            for idx, tv_show in enumerate(tv_shows[:10]):  # Show top 10
                title = tv_show.get("name", "Unknown")
                poster_path = tv_show.get("poster_path", "")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/180x270"
                item_id = tv_show.get("id")
                
                with cols[idx % 5]:
                    details_url = f"/details?media_type=tv&id={item_id}"
                    st.markdown(f"[![{title}]({poster_url})]({details_url})", unsafe_allow_html=True)
                    st.write(title)
        else:
            st.write("❌ No TV show recommendations found for this mood.")
    else:
        st.write("❌ No matching genres found for this emoji.")