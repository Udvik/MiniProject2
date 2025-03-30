import streamlit as st
import requests
import os
from db import add_watched_content, add_liked_content



# Initialize session state if not exists
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False,
        'username': '',
        'preferences': []
    })


API_KEY = os.getenv("TMDB_API_KEY")

def fetch_details(media_type, item_id):
    base_url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    params = {"api_key": API_KEY}
    
    details = requests.get(base_url, params=params).json()
    providers = requests.get(f"{base_url}/watch/providers", params=params).json()
    
    return details, providers.get("results", {})

# Get parameters
media_type = st.query_params.get("media_type")
item_id = st.query_params.get("id")

if not media_type or not item_id:
    st.error("Missing parameters!")
    st.stop()

details, providers = fetch_details(media_type, item_id)

# Display Details
st.title(details.get("title") or details.get("name"))
st.image(f"https://image.tmdb.org/t/p/w500{details.get('poster_path')}", 
        use_container_width=True)

st.subheader("Overview")
st.write(details.get("overview", "No description available."))

if media_type == "movie":
    st.markdown(f"**Release Date:** 📅 {details.get('release_date')}")
else:
    st.markdown(f"**First Air Date:** 📅 {details.get('first_air_date')}")

st.markdown(f"**Rating:** ⭐ {details.get('vote_average', 'N/A')}/10")

# Watch Providers
st.subheader("Where to Watch")
allowed_countries = {
    "IN": "🇮🇳 India",
    "US": "🇺🇸 USA",
    "GB": "🇬🇧 UK",
    "AU": "🇦🇺 Australia"
}

cols = st.columns(len(allowed_countries))
for idx, (code, name) in enumerate(allowed_countries.items()):
    with cols[idx]:
        st.markdown(f"**{name}**")
        if providers.get(code, {}).get("flatrate"):
            for provider in providers[code]["flatrate"]:
                st.image(f"https://image.tmdb.org/t/p/w500{provider['logo_path']}", 
                        width=50)
                st.write(provider["provider_name"])
        else:
            st.write("❌ Not available")

# Watched/Liked Buttons
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("✅ Mark as Watched"):
        if st.session_state.logged_in:
            add_watched_content(
                st.session_state.username,
                media_type,
                item_id,
                details.get("title") or details.get("name")
            )
            st.success("Added to watched list!")
        else:
            st.error("Please login first")

with col2:
    if st.button("❤️ Add to Liked"):
        if st.session_state.logged_in:
            add_liked_content(
                st.session_state.username,
                media_type,
                item_id,
                details.get("title") or details.get("name")
            )
            st.success("Added to liked list!")
        else:
            st.error("Please login first")

if st.button("← Back"):
    st.switch_page("pages/home.py")