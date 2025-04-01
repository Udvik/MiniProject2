import streamlit as st
from db import get_user_content
import requests
import os

# Set page config FIRST
st.set_page_config(layout="wide")

# Add the padding CSS
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > .main {
        padding: 2rem 5rem !important;
    }
    @media (max-width: 768px) {
        [data-testid="stAppViewContainer"] > .main {
            padding: 2rem 1rem !important;
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

def remove_content(username, content_type, item_id):
    """Remove item from watched or liked list"""
    from db import users_collection
    
    update_result = users_collection.update_one(
        {"username": username},
        {"$pull": {content_type: {"id": item_id}}}
    )
    return update_result.modified_count > 0

# Get content type from session state
content_type = st.session_state.get("list_content_type", "watched")

st.title(f"Your {content_type.capitalize()} Content")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to view this content")
    st.stop()

content = get_user_content(st.session_state.username)[content_type]

if not content:
    st.info(f"You haven't {content_type} anything yet")
else:
    cols = st.columns(4)
    for idx, item in enumerate(content):  # Using enumerate to get unique index
        with cols[idx % 4]:
            poster_path = fetch_poster(item["type"], item["id"])
            title = item["title"]
            
            if poster_path:
                st.image(
                    f"https://image.tmdb.org/t/p/w500{poster_path}",
                    width=150,
                    caption=title
                )
            else:
                st.image(
                    "https://via.placeholder.com/150x225?text=No+Poster",
                    width=150,
                    caption=title
                )
            
            # Modified button with unique key using index
            if st.button(f"Remove from {content_type}", 
                        key=f"remove_{content_type}_{item['id']}_{idx}"):  # Added index to key
                if remove_content(st.session_state.username, content_type, item["id"]):
                    st.success(f"Removed {title} from your {content_type} list!")
                    st.rerun()
                else:
                    st.error("Failed to remove item")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")