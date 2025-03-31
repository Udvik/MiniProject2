import streamlit as st
from db import (
    get_friends,
    get_friend_requests,
    send_friend_request,
    respond_friend_request
)

# Set page config
st.set_page_config(page_title="Friends", layout="wide")

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
    st.warning("Please log in to access friends")
    st.stop()

username = st.session_state.username

# Friend Requests Section
st.title("👥 Friends Management")

st.header("📨 Friend Requests")
requests = get_friend_requests(username)
if requests:
    for req in requests:
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

# Add Friend Section
st.header("➕ Add Friend")
new_friend = st.text_input("Enter username to add as friend")
if st.button("Send Friend Request"):
    if send_friend_request(username, new_friend):
        st.success(f"Friend request sent to {new_friend}")
    else:
        st.error("Could not send friend request")

# Friends List Section
st.header("🤝 Your Friends")
friends = get_friends(username)
if friends:
    for friend in friends:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(friend)
        with col2:
            if st.button("View Profile", key=f"view_{friend}"):
                st.session_state._current_friend = friend
                st.switch_page("pages/friend_profile.py")
else:
    st.info("You haven't added any friends yet")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")