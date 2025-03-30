import streamlit as st
import requests
import os
from db import get_user_content

# Set page config FIRST (must be first Streamlit command)
st.set_page_config(page_title="Dashboard", layout="wide")

# TMDB API Configuration
API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Add padding CSS to match home page
st.markdown("""
<style>
    .main {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .st-emotion-cache-1y4p8pa {
        padding: 1rem;
    }
    /* Ensure padding persists - uses same selector as app.py */
    [data-testid="stAppViewContainer"] > .main {
        padding: 2rem 5rem !important;
    }
    
    @media (max-width: 768px) {
        [data-testid="stAppViewContainer"] > .main {
            padding: 2rem 1rem !important;
        }
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def fetch_poster(media_type, item_id):
    API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    response = requests.get(url, params={"api_key": API_KEY})
    if response.status_code == 200:
        return response.json().get("poster_path")
    return None

# Authentication Check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access the dashboard")
    st.stop()

# Get username from session
username = st.session_state.get("username", "Guest")

# Streamlit UI
st.title(f"Welcome back, {username}!")

# User Profile Section
st.markdown("## 👤 Your Profile")
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("""
    <div style="background-color: #000; width: 100px; height: 100px; 
                border-radius: 50%; display: flex; align-items: center; 
                justify-content: center; margin-bottom: 10px;">
        <span style="color: white; font-size: 40px;">👤</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    - **Username:** {username}
    - **Favorite Genres:** {', '.join(st.session_state.preferences) if st.session_state.preferences else 'Not specified'}
    """)
if st.button("Logout", key="dashboard_logout"):
        st.session_state.update({
            "logged_in": False,
            "username": "",
            "preferences": [],
            "_session_id": None,
            "_pending_details": None
        })
        st.markdown("""
        <script>
        localStorage.removeItem('streamlit_login');
        localStorage.removeItem('streamlit_username');
        window.location.href = '/';
        </script>
        """, unsafe_allow_html=True)

st.markdown("---")

# Watched Content Section
st.markdown("## 🎬 Your Watched Content")
watched_content = get_user_content(username)["watched"]
if watched_content:
    cols = st.columns(4)
    for idx, item in enumerate(watched_content[:4]):
        with cols[idx % 4]:
            poster_path = fetch_poster(item["type"], item["id"])
            if poster_path:
                st.image(
                    f"{TMDB_IMAGE_BASE_URL}{poster_path}",
                    width=150,
                    caption=item["title"]
                )
            else:
                st.image(
                    "https://via.placeholder.com/150x225?text=No+Poster",
                    width=150,
                    caption=item["title"]
                )
    if len(watched_content) > 4:
        if st.button("View All Watched →", key="view_all_watched"):
            st.session_state.list_content_type = "watched"
            st.switch_page("pages/list_content.py")
else:
    st.info("You haven't watched anything yet")

st.markdown("---")

# Liked Content Section
st.markdown("## ❤️ Your Liked Content")
liked_content = get_user_content(username)["liked"]
if liked_content:
    cols = st.columns(4)
    for idx, item in enumerate(liked_content[:4]):
        with cols[idx % 4]:
            poster_path = fetch_poster(item["type"], item["id"])
            if poster_path:
                st.image(
                    f"{TMDB_IMAGE_BASE_URL}{poster_path}",
                    width=150,
                    caption=item["title"]
                )
            else:
                st.image(
                    "https://via.placeholder.com/150x225?text=No+Poster",
                    width=150,
                    caption=item["title"]
                )
    if len(liked_content) > 4:
        if st.button("View All Liked →", key="view_all_liked"):
            st.session_state.list_content_type = "liked"
            st.switch_page("pages/list_content.py")
else:
    st.info("You haven't liked anything yet")

if st.button("← Back to Home"):
    st.switch_page("pages/home.py")