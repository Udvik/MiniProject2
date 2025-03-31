import streamlit as st
from db import (
    get_friends,
    get_recommendations,
    add_recommendation,
    remove_recommendation
)

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
    item_id = st.text_input("TMDB ID")
    title = st.text_input("Title")
    note = st.text_area("Personal Note (optional)")
    
    if st.button("Send Recommendation"):
        if add_recommendation(username, friend, media_type, item_id, title, note):
            st.success("Recommendation sent successfully!")
        else:
            st.error("Failed to send recommendation")
else:
    st.info("Add friends to send recommendations")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")