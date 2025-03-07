import streamlit as st
import requests
import os

# TMDB API Key
API_KEY = os.getenv("TMDB_API_KEY")

# API Endpoints
POPULAR_MOVIES_URL = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}"
SEARCH_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"

# Function to fetch popular movies
def fetch_popular_movies():
    response = requests.get(POPULAR_MOVIES_URL)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

# Function to search movies
def search_movies(query):
    params = {"api_key": API_KEY, "query": query}
    response = requests.get(SEARCH_MOVIE_URL, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

# Streamlit UI
st.title("🎬 Movie Explorer")
st.write("Browse Popular Movies or Search for Any Movie")

# Search Bar
query = st.text_input("🔍 Search for a movie...")

# If user enters a search query
if query:
    movies = search_movies(query)
else:
    movies = fetch_popular_movies()

# Display Movies
cols = st.columns(4)  # Create 4 columns per row

for i, movie in enumerate(movies):
    if movie.get("poster_path"):  # Ensure poster exists
        with cols[i % 4]:  # Arrange in columns
            st.image(
                f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", 
                use_container_width=True  # ✅ Updated parameter
            )
            st.caption(movie["title"])  # Show title under poster
