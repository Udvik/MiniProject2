import streamlit as st
import requests
import os
from dotenv import load_dotenv
from transformers import pipeline
#testing
# Load API Key from .env
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    st.error("API Key not found! Make sure to set it in the .env file.")
    st.stop()

# TMDB URLs
TMDB_GENRES_LIST_URL = "https://api.themoviedb.org/3/genre/movie/list"
TMDB_MOVIES_URL = "https://api.themoviedb.org/3/discover/movie"

# Mood-to-Genre Mapping
MOOD_TO_GENRE = {
    "joy": ["Documentary", "History"],    
    "sadness": ["Comedy", "Adventure", "Animation"],   
    "anger": ["Drama", "Romance"],  
    "fear": ["Comedy", "Drama"],  
    "surprise": ["Action", "Thriller"],   
    "neutral": ["Science Fiction", "Fantasy"],    
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

# Load Sentiment Model
emotion_classifier = pipeline("text-classification", model="seara/rubert-tiny2-ru-go-emotions")

# Streamlit UI
st.title("🎬 AI Movie Recommendation Chatbot")

user_input = st.text_input("How are you feeling today?")

if user_input:
    # Detect emotion
    detected_emotion = emotion_classifier(user_input)[0]["label"].lower()
    st.write(f"**Detected Emotion:** {detected_emotion.capitalize()}")

    # Get movie genres for detected mood
    movie_genres = MOOD_TO_GENRE.get(detected_emotion, [])
    genre_ids = [GENRE_MAPPING[genre] for genre in movie_genres if genre in GENRE_MAPPING]

    if genre_ids:
        movies = fetch_movies_by_genre(genre_ids)

        if movies:
            st.subheader("🎥 Recommended Movies")
            
            cols = st.columns(5)  # Display 5 movies per row
            for idx, movie in enumerate(movies[:15]):  # Show top 15 movies
                title = movie.get("title", "Unknown")
                poster_path = movie.get("poster_path", "")
                movie_id = movie.get("id")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/180x270"
                
                with cols[idx % 5]:
                    st.image(poster_url, width=150)
                    st.write(title)
        else:
            st.write("❌ Sorry, no recommendations found.")
    else:
        st.write("❌ No matching genres found for this mood.")
