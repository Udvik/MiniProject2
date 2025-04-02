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

# Function to display content with expand/shrink option
def display_content_section(title, icon, content, content_type="watched"):
    st.markdown(f"## {icon} {title}")
    
    if not content:
        st.info(f"You haven't {title.lower()} anything yet.")
        return
    
    # Initialize session state for expanded view if not exists
    if f"show_all_{content_type}" not in st.session_state:
        st.session_state[f"show_all_{content_type}"] = False
    
    # Determine how many items to show
    show_all = st.session_state[f"show_all_{content_type}"]
    items_to_show = content if show_all else content[:8]
    
    # Display content
    cols = st.columns(4)
    for idx, item in enumerate(items_to_show):
        with cols[idx % 4]:
            poster_path = fetch_poster(item["type"] if content_type != "recommendations" else item["media_type"], 
                                    item["id"] if content_type != "recommendations" else item["item_id"])
            details_url = f"/details?media_type={item['type'] if content_type != 'recommendations' else item['media_type']}&id={item['id'] if content_type != 'recommendations' else item['item_id']}"
            
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
            
            if content_type == "recommendations":
                st.caption(f"{item['title']} (from {item['from_user']})")
            else:
                st.caption(item["title"])
    
    # Show expand/shrink button if there are more than 8 items
    if len(content) > 8:
        if st.button("Show All" if not show_all else "Show Less", 
                    key=f"toggle_{content_type}"):
            st.session_state[f"show_all_{content_type}"] = not st.session_state[f"show_all_{content_type}"]
            st.rerun()

# Display Watched Content
display_content_section("Watched Content", "🎬", watched_content, "watched")

# Display Liked Content
display_content_section("Liked Content", "❤️", liked_content, "liked")

# Display Recommendations
display_content_section("Recommendations", "💌", recommendations, "recommendations")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")