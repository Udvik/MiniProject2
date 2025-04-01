import time
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
TMDB_MOVIES_URL = "https://api.themoviedb.org/3/discover/movie"
TMDB_TV_URL = "https://api.themoviedb.org/3/discover/tv"  # URL to fetch TV shows

# Emoji-to-Genre Mapping with Movie and TV Show Genre Names
EMOJI_TO_GENRE_MOVIES = {
    ("😀", "😢", "😊", "🤗"): ["Comedy", "Adventure"],  # Happy & comforting movies
    ("😡", "🤬"): ["Action", "Thriller"],  # Angry moods → Action-packed movies
    ("😱", "👻", "🎃"): ["Horror", "Mystery"],  # Scary moods → Horror films
    ("😮", "🤯"): ["Sci-Fi", "Fantasy"],  # Mind-blowing, futuristic vibes
    ("😐", "📜", "🤓"): ["Documentary", "History"],  # Informational movies
    ("❤️", "💔", "🥰"): ["Romance", "Drama"],  # Love & heartbreak themes
    ("🎶"): ["Music", "Musical"],  # Music and dance-themed movies
}

EMOJI_TO_GENRE_TV = {
    ("😀", "😢", "😊", "🤗"): ["Comedy", "Drama"],  # Happy & comforting TV shows
    ("😡", "🤬"): ["Action & Adventure", "Thriller"],  # Angry moods → Action-packed TV shows
    ("😱", "👻", "🎃"): ["Horror", "Mystery"],  # Scary moods → Horror TV shows
    ("😮", "🤯"): ["Sci-Fi & Fantasy", "Drama"],  # Mind-blowing, futuristic vibes
    ("😐", "📜", "🤓"): ["Documentary", "History"],  # Informational TV shows
    ("❤️", "💔", "🥰"): ["Romance", "Drama"],  # Love & heartbreak themes
    ("🎶"): ["Music", "Reality"],  # Music and dance-themed TV shows
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

# Fetch Movies and TV Shows by Genre
def fetch_movies_and_tv_by_genre(genre_ids, content_type="movie"):
    try:
        if content_type == "movie":
            url = TMDB_MOVIES_URL
        elif content_type == "tv":
            url = TMDB_TV_URL
        
        params = {"api_key": API_KEY, "with_genres": ",".join(map(str, genre_ids))}
        response = requests.get(url, params=params, timeout=10)  # Timeout set to 10 seconds
        
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            st.error(f"Error fetching data from TMDB API (Status code: {response.status_code}).")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return []

# Streamlit UI
st.title("🎬 Emoji-Based Movie & TV Show Recommendation")

selected_emoji = st.selectbox("Select your current mood:", list(emoji for emojis in EMOJI_TO_GENRE_MOVIES.keys() for emoji in emojis))

if selected_emoji:
    st.write(f"**Detected Emotion:** {emoji.demojize(selected_emoji).replace(':', '').capitalize()}")

    # Find the genre list based on emoji selection
    movie_genres = next((genres for key, genres in EMOJI_TO_GENRE_MOVIES.items() if selected_emoji in key), [])
    tv_genres = next((genres for key, genres in EMOJI_TO_GENRE_TV.items() if selected_emoji in key), [])

    if movie_genres or tv_genres:
        movie_genre_ids = [GENRE_MAPPING[genre] for genre in movie_genres if genre in GENRE_MAPPING]
        tv_genre_ids = [GENRE_MAPPING[genre] for genre in tv_genres if genre in GENRE_MAPPING]

        # Fetch both movies and TV shows (combining both)
        movies = fetch_movies_and_tv_by_genre(movie_genre_ids, content_type="movie")
        tv_shows = fetch_movies_and_tv_by_genre(tv_genre_ids, content_type="tv")

        if movies or tv_shows:
            # Randomly select 10 movies and 10 TV shows
            random_movies = random.sample(movies, min(10, len(movies)))  # 10 random movies
            random_tv_shows = random.sample(tv_shows, min(10, len(tv_shows)))  # 10 random TV shows

            # Show Movies Section
            st.subheader("🎥 Recommended Movies")
            cols = st.columns(5)  # Display 5 per row for Movies
            for idx, movie in enumerate(random_movies):  # Show selected random movies
                title = movie.get("title", "Unknown")
                poster_path = movie.get("poster_path", "")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/180x270"
                
                with cols[idx % 5]:
                    st.image(poster_url, width=150)
                    st.write(title)

            # Show TV Shows Section
            st.subheader("📺 Recommended TV Shows")
            cols = st.columns(5)  # Display 5 per row for TV Shows
            for idx, tv_show in enumerate(random_tv_shows):  # Show selected random TV shows
                title = tv_show.get("name", "Unknown")
                poster_path = tv_show.get("poster_path", "")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/180x270"
                
                with cols[idx % 5]:
                    st.image(poster_url, width=150)
                    st.write(title)

        else:
            st.write("❌ Sorry, no recommendations found.")
    else:
        st.write("❌ No matching genres found for this emoji.")
