import streamlit as st
import requests
import os


st.markdown("""
<style>
    .stCaption {
        font-size: 14px !important;
        text-align: center !important;
        margin-top: 8px !important;
    }
    img:hover {
        opacity: 0.9;
        transition: opacity 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# --- Function Definitions FIRST ---
def display_content(items, media_type):
    cols = st.columns(4)
    for i, item in enumerate(items[:8]):
        with cols[i % 4]:
            poster_path = item.get("poster_path")
            title = (item.get("title") or item.get("name"))[:20] + "..." if len(item.get("title") or item.get("name")) > 20 else (item.get("title") or item.get("name"))
            item_id = item.get("id")
            
            # Container with minimal spacing
            if poster_path and item_id:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                details_url = f"/details?media_type={media_type}&id={item_id}"
                st.markdown(
                    f'<a href="{details_url}" target="_self" style="display:block; margin-bottom:8px;">'
                    f'<img src="{poster_url}" style="width:100%; height:auto; aspect-ratio:2/3; object-fit:cover; border-radius:8px;"></a>',
                    unsafe_allow_html=True
                )
            else:
                # Placeholder matching poster aspect ratio
                st.markdown(
                    '<div style="width:100%; aspect-ratio:2/3; background:#eee; border-radius:8px; display:flex; '
                    'align-items:center; justify-content:center; margin-bottom:8px;">'
                    '<span style="color:#666;">No Image</span></div>',
                    unsafe_allow_html=True
                )
            
            st.caption(title)

def fetch_popular_movies():
    API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}"
    response = requests.get(url)
    return response.json().get("results", []) if response.status_code == 200 else []

def fetch_popular_tv():
    API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}"
    response = requests.get(url)
    return response.json().get("results", []) if response.status_code == 200 else []

def search_content(query):
    API_KEY = os.getenv("TMDB_API_KEY")
    url = "https://api.themoviedb.org/3/search/multi"
    params = {"api_key": API_KEY, "query": query}
    response = requests.get(url, params=params)
    return response.json().get("results", []) if response.status_code == 200 else []

# --- Streamlit UI Code AFTER functions ---
st.title("🎬 Entertainment Explorer")
query = st.text_input("🔍 Search for movies or TV shows...")

if query:
    results = search_content(query)
    movies = [r for r in results if r.get("media_type") == "movie"]
    tv_shows = [r for r in results if r.get("media_type") == "tv"]
    
    if movies:
        st.subheader("Movies")
        display_content(movies, "movie")
    
    if tv_shows:
        st.subheader("TV Shows")
        display_content(tv_shows, "tv")
else:
    st.subheader("Popular Movies")
    movies = fetch_popular_movies()
    display_content(movies, "movie")
    
    st.subheader("Popular TV Shows")
    tv_shows = fetch_popular_tv()
    display_content(tv_shows, "tv")