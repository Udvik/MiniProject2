import streamlit as st
import requests
import os
from db import (
    get_user_content, 
    send_friend_request, 
    get_friend_requests,
    respond_friend_request,
    get_friends,
    get_recommendations,
    remove_recommendation
)

# Set page config
st.set_page_config(page_title="Dashboard", layout="wide")

# TMDB API Configuration
API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# CSS Styling
st.markdown("""
<style>
    .main {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .st-emotion-cache-1y4p8pa {
        padding: 1rem;
    }
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
    .poster-container {
        position: relative;
        margin-bottom: 8px;
    }
    .poster-container img {
        transition: transform 0.2s;
    }
    .poster-container img:hover {
        transform: scale(1.03);
        cursor: pointer;
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

# Friend System Section
st.markdown("---")
st.markdown("## 🤝 Friends")

# Friend Requests
st.markdown("### Friend Requests")
friend_requests = get_friend_requests(username)
if friend_requests:
    for req in friend_requests:
        if req["to_user"] == username:  # Incoming requests
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"Friend request from: {req['from_user']}")
            with col2:
                if st.button("Accept", key=f"accept_{req['_id']}"):
                    respond_friend_request(req["_id"], "accept")
                    st.rerun()
            with col3:
                if st.button("Reject", key=f"reject_{req['_id']}"):
                    respond_friend_request(req["_id"], "reject")
                    st.rerun()
else:
    st.info("No pending friend requests")

# Add Friend
st.markdown("### Add Friend")
new_friend = st.text_input("Enter username to add as friend")
if st.button("Send Friend Request"):
    if send_friend_request(username, new_friend):
        st.success(f"Friend request sent to {new_friend}")
    else:
        st.error("Could not send friend request")

# Friends List
st.markdown("### Your Friends")
friends = get_friends(username)
if friends:
    for friend in friends:
        st.write(friend)
else:
    st.info("You haven't added any friends yet")

# Recommendations Section
st.markdown("---")
st.markdown("## 💌 Recommendations")

# Received Recommendations - showing last 4 recent recommendations
st.markdown("### Recommendations for You")
recommendations = get_recommendations(username)
if recommendations:
    # Reverse to show most recent first
    recommendations.reverse()
    cols = st.columns(4)
    for idx, rec in enumerate(recommendations[:4]):
        with cols[idx % 4]:
            poster_path = fetch_poster(rec["media_type"], rec["item_id"])
            details_url = f"/details?media_type={rec['media_type']}&id={rec['item_id']}"
            
            if poster_path:
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{TMDB_IMAGE_BASE_URL}{poster_path}" width="150" alt="{rec["title"]}">'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="https://via.placeholder.com/150x225?text=No+Poster" width="150" alt="{rec["title"]}">'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.caption(f"{rec['title']} (from {rec['from_user']})")
            if st.button("Remove", key=f"remove_rec_{rec['_id']}"):
                remove_recommendation(rec["_id"])
                st.rerun()
    
    # View more button styled like other "View All" buttons
    if st.button("View All Recommendations →", key="view_all_recommendations"):
        st.switch_page("pages/recommendations.py")
else:
    st.info("No recommendations for you yet")
    if st.button("View Recommendations →", key="view_recommendations"):
        st.switch_page("pages/recommendations.py")

# Watched Content Section with clickable posters
st.markdown("---")
st.markdown("## 🎬 Your Watched Content")
watched_content = get_user_content(username).get("watched", [])

watched_content.reverse()

if watched_content:
    cols = st.columns(4)
    for idx, item in enumerate(watched_content[:4]):
        with cols[idx % 4]:
            poster_path = fetch_poster(item["type"], item["id"])
            details_url = f"/details?media_type={item['type']}&id={item['id']}"
            
            if poster_path:
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{TMDB_IMAGE_BASE_URL}{poster_path}" width="150" alt="{item["title"]}">'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="https://via.placeholder.com/150x225?text=No+Poster" width="150" alt="{item["title"]}">'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.caption(item["title"])
    if len(watched_content) > 4:
        if st.button("View All Watched →", key="view_all_watched"):
            st.session_state.list_content_type = "watched"
            st.switch_page("pages/list_content.py")
else:
    st.info("You haven't watched anything yet")

# Liked Content Section with clickable posters
st.markdown("---")
st.markdown("## ❤️ Your Liked Content")

liked_content = get_user_content(username).get("liked", [])

liked_content.reverse()

if liked_content:
    cols = st.columns(4)
    for idx, item in enumerate(liked_content[:4]):
        with cols[idx % 4]:
            poster_path = fetch_poster(item["type"], item["id"])
            details_url = f"/details?media_type={item['type']}&id={item['id']}"
            
            if poster_path:
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{TMDB_IMAGE_BASE_URL}{poster_path}" width="150" alt="{item["title"]}">'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="poster-container">'
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="https://via.placeholder.com/150x225?text=No+Poster" width="150" alt="{item["title"]}">'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.caption(item["title"])
    if len(liked_content) > 4:
        if st.button("View All Liked →", key="view_all_liked"):
            st.session_state.list_content_type = "liked"
            st.switch_page("pages/list_content.py")
else:
    st.info("You haven't liked anything yet")

if st.button("← Back to Home"):
    st.switch_page("pages/home.py")