import streamlit as st
from db import register_user, login_user
from streamlit_option_menu import option_menu

# Custom CSS to COMPLETELY hide auto-generated menu and style our custom menu
st.markdown("""
<style>
    /* 1. Completely hide Streamlit's default menu */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* 2. Style for our custom menu */
    .st-emotion-cache-16txtl3 {
        padding: 1rem !important;
    }
    /* Make menu items full width */
    .stButton>button {
        width: 100% !important;
        justify-content: left !important;
        padding: 8px 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["preferences"] = []

# Custom sidebar menu - Only shows what we explicitly define
with st.sidebar:
    st.title("Menu")
    
    if st.session_state["logged_in"]:
        menu_choice = option_menu(
            menu_title=None,
            options=["Home", "Logout"],  # Only these two when logged in
            icons=["house", "box-arrow-right"],
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0!important"
                }
            }
        )
    else:
        menu_choice = option_menu(
            menu_title=None,
            options=["Login", "Register"],  # Only these two when logged out
            icons=["box-arrow-in-right", "person-plus"],
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0!important"
                }
            }
        )

# Handle navigation
if menu_choice == "Home" and st.session_state["logged_in"]:
    st.switch_page("pages/home.py")
    
elif menu_choice == "Login":
    st.subheader("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["preferences"] = user["preferences"]
            st.success(f"Welcome, {username}! Redirecting...")
            st.switch_page("pages/home.py")
        else:
            st.error("Invalid username or password")

elif menu_choice == "Register":
    st.subheader("Register New User")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    
    genres = ["Comedy", "Horror", "Sci-Fi", "Action", "Drama", "Romance"]
    preferences = st.multiselect("Select Your Favorite Genres", genres)

    if st.button("Register"):
        if register_user(new_username, new_password, preferences):
            st.success("Registration successful! Please log in.")
        else:
            st.error("Username already exists")

elif menu_choice == "Logout":
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["preferences"] = []
    st.success("Logged out successfully!")
    st.experimental_rerun()  # Refresh to show login screen