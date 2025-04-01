import streamlit as st
import requests
import os
from db import get_user_content, get_recommendations

# Set page config
st.set_page_config(page_title="History", layout="wide")

# TMDB API Configuration
API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Function to fetch poster
def fetch_poster(media_type, item_id):
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    try:
        response = requests.get(url, params={"api_key": API_KEY}, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json().get("poster_path")
        else:
            st.error(f"Error fetching poster: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {str(e)}")
    return None

# Authentication Check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access your history")
    st.stop()

# Get username from session
username = st.session_state.get("username", "Guest")

# Streamlit UI
st.title(f"Your Collection, {username}!")

# Fetch Content from Database
user_content = get_user_content(username)
watched_content = user_content.get("watched", [])
liked_content = user_content.get("liked", [])
recommendations = get_recommendations(username)

# Reverse the lists to display the most recent first
watched_content.reverse()
liked_content.reverse()
recommendations.reverse()

# Display Watched Content with clickable posters
st.markdown("## 🎬 Watched Content")
if watched_content:
    cols = st.columns(4)
    for idx, item in enumerate(watched_content):
        with cols[idx % 4]:
            poster_path = fetch_poster(item["type"], item["id"])
            details_url = f"/details?media_type={item['type']}&id={item['id']}"
            
            if poster_path:
                st.markdown(
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{TMDB_IMAGE_BASE_URL}{poster_path}" width="150" style="border-radius:8px;margin-bottom:8px;">'
                    f'</a>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="https://via.placeholder.com/150x225?text=No+Poster" width="150" style="border-radius:8px;margin-bottom:8px;">'
                    f'</a>',
                    unsafe_allow_html=True
                )
            st.caption(item["title"])
else:
    st.info("You haven't watched anything yet.")

# Display Liked Content with clickable posters
st.markdown("## ❤️ Liked Content")
if liked_content:
    cols = st.columns(4)
    for idx, item in enumerate(liked_content):
        with cols[idx % 4]:
            poster_path = fetch_poster(item["type"], item["id"])
            details_url = f"/details?media_type={item['type']}&id={item['id']}"
            
            if poster_path:
                st.markdown(
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{TMDB_IMAGE_BASE_URL}{poster_path}" width="150" style="border-radius:8px;margin-bottom:8px;">'
                    f'</a>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="https://via.placeholder.com/150x225?text=No+Poster" width="150" style="border-radius:8px;margin-bottom:8px;">'
                    f'</a>',
                    unsafe_allow_html=True
                )
            st.caption(item["title"])
else:
    st.info("You haven't liked anything yet.")

# Display Recommendations with clickable posters
st.markdown("## 💌 Recommendations")
if recommendations:
    cols = st.columns(4)
    for idx, rec in enumerate(recommendations):
        with cols[idx % 4]:
            poster_path = fetch_poster(rec["media_type"], rec["item_id"])
            details_url = f"/details?media_type={rec['media_type']}&id={rec['item_id']}"
            
            if poster_path:
                st.markdown(
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{TMDB_IMAGE_BASE_URL}{poster_path}" width="150" style="border-radius:8px;margin-bottom:8px;">'
                    f'</a>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="https://via.placeholder.com/150x225?text=No+Poster" width="150" style="border-radius:8px;margin-bottom:8px;">'
                    f'</a>',
                    unsafe_allow_html=True
                )
            st.caption(f"{rec['title']} (from {rec['from_user']})")
else:
    st.info("No recommendations for you yet.")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")