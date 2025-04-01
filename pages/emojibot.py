import streamlit as st
import requests
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
TMDB_MOVIES_URL = "https://api.themoviedb.org/3/discover/movie"

# Emoji-to-Genre Mapping with Tuples for Multiple Emoji Handling
EMOJI_TO_GENRE = {
    ("😀", "😢", "😊", "🤗"): ["Comedy", "Adventure"],  # Happy & comforting movies
    ("😡", "🤬"): ["Action", "Thriller"],  # Angry moods → Action-packed movies
    ("😱", "👻", "🎃"): ["Horror", "Mystery"],  # Scary moods → Horror films
    ("😮", "🤯", "🚀"): ["Sci-Fi", "Fantasy"],  # Mind-blowing, futuristic vibes
    ("😐", "📜", "🤓"): ["Documentary", "History"],  # Informational movies
    ("❤️", "💔", "🥰"): ["Romance", "Drama"],  # Love & heartbreak themes
    ("🎶", "🎤", "🕺"): ["Music", "Musical"],  # Music and dance-themed movies
}

# Fetch TMDB Genre Mapping
@st.cache_data
def fetch_genre_mapping():
    response = requests.get(TMDB_GENRES_LIST_URL, params={"api_key": API_KEY})
    if response.status_code == 200:
        genres = response.json().get("genres", [])
        return {genre["name"]: genre["id"] for genre in genres}
    return {}

GENRE_MAPPING = fetch_genre_mapping()

# Fetch Movies by Genre
def fetch_movies_by_genre(genre_ids):
    url = TMDB_MOVIES_URL
    params = {"api_key": API_KEY, "with_genres": ",".join(map(str, genre_ids))}
    response = requests.get(url, params=params)
    return response.json().get("results", []) if response.status_code == 200 else []

# Streamlit UI
st.title("🎬 Emoji-Based Movie Recommendation")

selected_emoji = st.selectbox("Select your current mood:", list(emoji for emojis in EMOJI_TO_GENRE.keys() for emoji in emojis))

if selected_emoji:
    st.write(f"**Detected Emotion:** {emoji.demojize(selected_emoji).replace(':', '').capitalize()}")

    # Find the genre list based on emoji selection
    movie_genres = next((genres for key, genres in EMOJI_TO_GENRE.items() if selected_emoji in key), [])

    if movie_genres:
        genre_ids = [GENRE_MAPPING[genre] for genre in movie_genres if genre in GENRE_MAPPING]

        if genre_ids:
            movies = fetch_movies_by_genre(genre_ids)

            if movies:
                st.subheader("🎥 Recommended Movies")
                cols = st.columns(5)  # Display 5 movies per row
                for idx, movie in enumerate(movies[:15]):  # Show top 15 movies
                    title = movie.get("title", "Unknown")
                    poster_path = movie.get("poster_path", "")
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/180x270"
                    
                    with cols[idx % 5]:
                        st.image(poster_url, width=150)
                        st.write(title)
            else:
                st.write("❌ Sorry, no recommendations found.")
        else:
            st.write("❌ No matching genres found for this emoji.")
    else:
        st.write("❌ No matching genres found for this emoji.")
