import streamlit as st
import requests
import os
from db import (
    get_friends,
    get_recommendations,
    add_recommendation,
    remove_recommendation
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Set page config
st.set_page_config(page_title="Recommendations", layout="wide")

# Add padding CSS
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
    .recommendation-actions {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def search_tmdb(query, media_type):
    """Search TMDB for movies or TV shows matching the query"""
    url = f"https://api.themoviedb.org/3/search/{media_type}"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "en-US",
        "page": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        # Return list of (formatted_title, id) tuples sorted by popularity
        formatted_results = []
        for item in sorted(results, key=lambda x: x.get("popularity", 0), reverse=True):
            if media_type == "movie":
                year = item.get("release_date", "")[:4] if item.get("release_date") else "Unknown"
                title = f"{item['title']} ({year})" if year else item['title']
            else:
                year = item.get("first_air_date", "")[:4] if item.get("first_air_date") else "Unknown"
                title = f"{item['name']} ({year})" if year else item['name']
            formatted_results.append((title, item["id"]))
        return formatted_results
    return []

# Authentication Check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access recommendations")
    st.stop()

username = st.session_state.username

# Recommendations Page
st.title("💌 Recommendations")

# Received Recommendations
st.header("📩 Recommendations For You")
recommendations = get_recommendations(username)
if recommendations:
    for rec in recommendations:
        with st.expander(f"{rec['title']} (from {rec['from_user']})"):
            st.write(f"Type: {rec['media_type'].capitalize()}")
            if rec.get("note"):
                st.write(f"Note: {rec['note']}")
            
            # Action buttons container
            st.markdown('<div class="recommendation-actions">', unsafe_allow_html=True)
            
            # Details button
            details_url = f"/details?media_type={rec['media_type']}&id={rec['item_id']}"
            st.markdown(
                f'<a href="{details_url}" target="_blank">'
                '<button style="padding: 0.25rem 0.5rem; font-size: 0.9rem;">View Details</button>'
                '</a>',
                unsafe_allow_html=True
            )
            
            # Remove button
            if st.button("Remove", key=f"remove_{rec['_id']}"):
                remove_recommendation(rec["_id"])
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No recommendations for you yet")

# Send Recommendations
st.header("📤 Send Recommendation")
friends = get_friends(username)
if friends:
    friend = st.selectbox("Select friend", friends)
    media_type = st.selectbox("Content Type", ["movie", "tv"])
    
    # Title search with autocomplete
    title_query = st.text_input("Search for title")
    search_results = []
    
    if title_query and len(title_query) > 2:
        search_results = search_tmdb(title_query, media_type)
    
    selected_title = None
    selected_id = None
    
    if search_results:
        # Create a select box with search results (title with year and ID)
        options = [f"{title} (ID: {id})" for title, id in search_results]
        selected_option = st.selectbox("Select from search results", options)
        
        if selected_option:
            # Extract the original title without year for storage
            original_title = selected_option.split(" (ID: ")[0].split(" (20")[0].split(" (19")[0]
            selected_title = original_title.strip()
            selected_id = selected_option.split(" (ID: ")[1][:-1]
    
    # Display the selected title and ID (or allow manual entry)
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title", value=selected_title if selected_title else "")
    with col2:
        item_id = st.text_input("TMDB ID", value=selected_id if selected_id else "")
    
    note = st.text_area("Personal Note (optional)")
    
    if st.button("Send Recommendation"):
        if not title or not item_id:
            st.error("Please select or enter both title and TMDB ID")
        elif add_recommendation(username, friend, media_type, item_id, title, note):
            st.success("Recommendation sent successfully!")
        else:
            st.error("Failed to send recommendation")
else:
    st.info("Add friends to send recommendations")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")