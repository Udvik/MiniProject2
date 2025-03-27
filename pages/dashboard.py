import streamlit as st
import requests
import os

# TMDB API Configuration
API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
POPULAR_MOVIES_URL = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}"
POPULAR_TV_URL = f"https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}"

# Authentication Check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access the dashboard")
    st.stop()

# Get username from session
username = st.session_state.get("username", "Guest")

# Streamlit UI
st.set_page_config(page_title="Dashboard", layout="wide")
st.title(f"Welcome back, {username}!")

# User Profile Section
st.markdown("## 👤 Your Profile")
col1, col2 = st.columns([1, 3])

with col1:
    # Black profile icon
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
    - **Email:** not available
    - **Member since:** not available
    """)

st.markdown("---")

# Placeholder Sections
st.markdown("## 🎬 Your Watched Content")
st.info("Feature coming soon - your watched history will appear here")
st.markdown("---")

st.markdown("## ❤️ Your Liked Content")
st.info("Feature coming soon - your favorites will appear here")
st.markdown("---")

# Popular Content Section
st.markdown("## 🔥 Popular This Week")

def fetch_data(url):
    try:
        response = requests.get(url, timeout=5)
        return response.json().get("results", [])[:4]  # Show only 4 items
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return []

def display_mini_card(item, media_type):
    poster_path = item.get("poster_path")
    title = (item.get("title") or item.get("name", "Untitled"))[:15] + ("..." if len(item.get("title") or item.get("name", "")) > 15 else "")
    
    container = st.container(border=True)
    with container:
        if poster_path:
            st.image(
                f"{TMDB_IMAGE_BASE_URL}{poster_path}",
                width=120,
                caption=title
            )
        else:
            st.image(
                "https://via.placeholder.com/120x180?text=No+Poster",
                width=120,
                caption=title
            )
        
        if st.button("Details", key=f"pop_{media_type}_{item.get('id')}"):
            st.session_state["selected_item"] = item.get("id")
            st.session_state["selected_type"] = media_type
            st.switch_page("pages/_details.py")

# Display popular content
tab1, tab2 = st.tabs(["Movies", "TV Shows"])

with tab1:
    movies = fetch_data(POPULAR_MOVIES_URL)
    if movies:
        cols = st.columns(4)
        for i, movie in enumerate(movies):
            with cols[i % 4]:
                display_mini_card(movie, "movie")
    else:
        st.warning("No popular movies found")

with tab2:
    shows = fetch_data(POPULAR_TV_URL)
    if shows:
        cols = st.columns(4)
        for i, show in enumerate(shows):
            with cols[i % 4]:
                display_mini_card(show, "tv")
    else:
        st.warning("No popular TV shows found")

# Navigation fix - add this to all your pages
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")