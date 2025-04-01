import time
import requests
import random
import streamlit as st
import os
import emoji
from dotenv import load_dotenv
from db import add_watched_content, add_liked_content, get_user_content  # Ensure this is correctly imported

# Load API Key
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    st.error("API Key not found! Make sure to set it in the .env file.")
    st.stop()

# TMDB API URLs
TMDB_GENRES_LIST_URL = "https://api.themoviedb.org/3/genre/movie/list"
TMDB_MOVIES_URL = "https://api.themoviedb.org/3/discover/movie"
TMDB_TV_URL = "https://api.themoviedb.org/3/discover/tv"

# 🎭 **Emoji-to-Genre Mapping**
EMOJI_TO_GENRE_MOVIES = {
    ("😀", "😢", "😊", "🤗"): ["Comedy", "Adventure"],
    ("😡", "🤬"): ["Action", "Thriller"],
    ("😱", "👻", "🎃"): ["Horror", "Mystery"],
    ("😮", "🤯"): ["Sci-Fi", "Fantasy"],
    ("😐", "📜", "🤓"): ["Documentary", "History"],
    ("❤️", "💔", "🥰"): ["Romance", "Drama"],
    ("🎶",): ["Music", "Musical"],
}

EMOJI_TO_GENRE_TV = {
    ("😀", "😢", "😊", "🤗"): ["Comedy", "Drama"],
    ("😡", "🤬"): ["Action & Adventure", "Thriller"],
    ("😱", "👻", "🎃"): ["Horror", "Mystery"],
    ("😮", "🤯"): ["Sci-Fi & Fantasy", "Drama"],
    ("😐", "📜", "🤓"): ["Documentary", "History"],
    ("❤️", "💔", "🥰"): ["Romance", "Drama"],
    ("🎶",): ["Music", "Reality"],
}

# 🟢 Fetch TMDB Genre Mapping
@st.cache_data
def fetch_genre_mapping():
    response = requests.get(TMDB_GENRES_LIST_URL, params={"api_key": API_KEY})
    if response.status_code == 200:
        genres = response.json().get("genres", [])
        return {genre["name"]: genre["id"] for genre in genres}
    return {}

GENRE_MAPPING = fetch_genre_mapping()

# 🟢 Fetch Movies and TV Shows by Genre
@st.cache_data
def fetch_movies_and_tv_by_genre(genre_ids, content_type="movie"):
    url = TMDB_MOVIES_URL if content_type == "movie" else TMDB_TV_URL
    params = {"api_key": API_KEY, "with_genres": ",".join(map(str, genre_ids))}
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

# 🟢 Streamlit UI
st.title("🎬 Emoji-Based Movie & TV Show Recommendation")

# 🟢 Ensure User Session
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.warning("Please log in to save watched/liked movies!")
else:
    st.success(f"Logged in as {st.session_state.username}")

# Select Emoji Mood
selected_emoji = st.selectbox("Select your current mood:", 
    list(emoji for emojis in EMOJI_TO_GENRE_MOVIES.keys() for emoji in emojis))

# 🟢 Fetch Movies & TV Shows based on Emoji
if "last_selected_emoji" not in st.session_state:
    st.session_state.last_selected_emoji = None
    st.session_state.movies = []
    st.session_state.tv_shows = []

if selected_emoji and selected_emoji != st.session_state.last_selected_emoji:
    st.session_state.last_selected_emoji = selected_emoji
    movie_genres = next((genres for key, genres in EMOJI_TO_GENRE_MOVIES.items() if selected_emoji in key), [])
    tv_genres = next((genres for key, genres in EMOJI_TO_GENRE_TV.items() if selected_emoji in key), [])
    movie_genre_ids = [GENRE_MAPPING[genre] for genre in movie_genres if genre in GENRE_MAPPING]
    tv_genre_ids = [GENRE_MAPPING[genre] for genre in tv_genres if genre in GENRE_MAPPING]
    st.session_state.movies = fetch_movies_and_tv_by_genre(movie_genre_ids, content_type="movie")
    st.session_state.tv_shows = fetch_movies_and_tv_by_genre(tv_genre_ids, content_type="tv")

# 🟢 Display Movies
st.subheader("🎥 Recommended Movies")
for movie in st.session_state.movies[:10]:
    title = movie.get("title", "Unknown")
    item_id = movie.get("id")

    st.write(f"**{title}**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Watched", key=f"watched_{item_id}"):
            if st.session_state.username:
                add_watched_content(st.session_state.username, "movie", item_id, title)
                st.toast(f"Added {title} to watched list!")
            else:
                st.warning("Please log in to track watched content!")

    with col2:
        if st.button("❤️ Like", key=f"liked_{item_id}"):
            if st.session_state.username:
                add_liked_content(st.session_state.username, "movie", item_id, title)
                st.toast(f"Added {title} to liked list!")
            else:
                st.warning("Please log in to track liked content!")

# 🟢 Display TV Shows
st.subheader("📺 Recommended TV Shows")
for tv_show in st.session_state.tv_shows[:10]:
    title = tv_show.get("name", "Unknown")
    item_id = tv_show.get("id")

    st.write(f"**{title}**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Watched", key=f"watched_tv_{item_id}"):
            if st.session_state.username:
                add_watched_content(st.session_state.username, "tv", item_id, title)
                st.toast(f"Added {title} to watched list!")
            else:
                st.warning("Please log in to track watched content!")

    with col2:
        if st.button("❤️ Like", key=f"liked_tv_{item_id}"):
            if st.session_state.username:
                add_liked_content(st.session_state.username, "tv", item_id, title)
                st.toast(f"Added {title} to liked list!")
            else:
                st.warning("Please log in to track liked content!")
