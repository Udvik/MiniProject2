import streamlit as st
import requests
import os

# TMDB API Key
API_KEY = os.getenv("TMDB_API_KEY")

# API Endpoints
MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie/{}"
WATCH_PROVIDERS_URL = "https://api.themoviedb.org/3/movie/{}/watch/providers"

# Function to fetch movie details
def get_movie_details(movie_id):
    url = MOVIE_DETAILS_URL.format(movie_id)
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch where to watch (streaming services)
def get_watch_providers(movie_id):
    url = WATCH_PROVIDERS_URL.format(movie_id)
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json().get("results", {})
        return data
    return {}

# Read movie_id from URL parameters
movie_id = st.query_params.get("movie_id")


if not movie_id:
    st.error("Movie ID not provided!")
    st.stop()

# Fetch movie details
movie_details = get_movie_details(movie_id)
watch_providers = get_watch_providers(movie_id)

if not movie_details:
    st.error("Movie not found!")
    st.stop()

# Extract Movie Details
title = movie_details.get("title", "Unknown Title")
poster_path = movie_details.get("poster_path")
overview = movie_details.get("overview", "No description available.")
genres = ", ".join([genre["name"] for genre in movie_details.get("genres", [])])
rating = movie_details.get("vote_average", "N/A")
release_date = movie_details.get("release_date", "Unknown")
runtime = movie_details.get("runtime", "N/A")

# Display Movie Poster & Details
st.title(title)
st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", use_container_width=True)
st.subheader("Overview")
st.write(overview)
st.markdown(f"**Genres:** {genres}")
st.markdown(f"**Rating:** ⭐ {rating} / 10")
st.markdown(f"**Release Date:** 📅 {release_date}")
st.markdown(f"**Runtime:** ⏳ {runtime} minutes")

# Display Where to Stream (Filtered for Selected Countries)
st.subheader("Where to Watch")

allowed_countries = {
    "IN": "🇮🇳 India",
    "US": "🇺🇸 USA",
    "GB": "🇬🇧 UK",
    "AU": "🇦🇺 Australia"
}

# Create columns for each country
cols = st.columns(len(allowed_countries))

for idx, (country_code, country_name) in enumerate(allowed_countries.items()):
    providers = watch_providers.get(country_code, {}).get("flatrate", [])
    ott_link = watch_providers.get(country_code, {}).get("link", None)  # Extract watch link

    with cols[idx]:  # Arrange countries in columns
        st.markdown(f"**{country_name}**")  # Show country name
        
        if providers:
            for provider in providers:
                logo_url = f"https://image.tmdb.org/t/p/w500{provider['logo_path']}"
                provider_name = provider["provider_name"]

                # Make provider name clickable if OTT link is available
                if ott_link:
                    st.image(logo_url, width=50)
                    st.markdown(f"[{provider_name}]({ott_link})", unsafe_allow_html=True)
                else:
                    st.image(logo_url, width=50)
                    st.write(provider_name)
        else:
            st.write("❌ Not available")

# Future Features Section (Like/Dislike, etc.)
st.markdown("---")
st.markdown("🛠 **More features coming soon!** (Like/Dislike, Watchlist, etc.)")
