import streamlit as st
from db import get_user_content, add_recommendation
#Checking Changes

# Set page config
st.set_page_config(page_title="Friend Profile", layout="wide")

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
</style>
""", unsafe_allow_html=True)

# Authentication Check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to view profiles")
    st.stop()

if "_current_friend" not in st.session_state or not st.session_state._current_friend:
    st.warning("No friend selected")
    st.stop()

username = st.session_state.username
friend = st.session_state._current_friend

# Friend Profile Page
st.title(f"👤 {friend}'s Profile")

# Send Recommendation Section
st.header("💌 Send Recommendation")
media_type = st.selectbox("Content Type", ["movie", "tv"])
item_id = st.text_input("TMDB ID")
title = st.text_input("Title")
note = st.text_area("Personal Note (optional)")

if st.button("Send Recommendation"):
    if add_recommendation(username, friend, media_type, item_id, title, note):
        st.success("Recommendation sent successfully!")
    else:
        st.error("Failed to send recommendation")

# Friend's Content Sections
col1, col2 = st.columns(2)

with col1:
    st.header(f"🎬 {friend}'s Watched Content")
    content = get_user_content(friend)
    if content["watched"]:
        for item in content["watched"]:
            st.write(f"- {item['title']} ({item['type'].capitalize()})")
    else:
        st.info(f"{friend} hasn't watched anything yet")

with col2:
    st.header(f"❤️ {friend}'s Liked Content")
    if content["liked"]:
        for item in content["liked"]:
            st.write(f"- {item['title']} ({item['type'].capitalize()})")
    else:
        st.info(f"{friend} hasn't liked anything yet")

if st.button("← Back to Friends"):
    st.session_state._current_friend = None
    st.switch_page("pages/friends.py")