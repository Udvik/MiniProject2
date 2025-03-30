import streamlit as st
from db import register_user, login_user
from streamlit_option_menu import option_menu
import time

# Custom CSS
st.markdown("""
<style>
    /* GLOBAL STYLES PERSISTENT ACROSS NAVIGATION */
    [data-testid="stAppViewContainer"] > .main {
        padding: 2rem 5rem !important;
    }
    
    @media (max-width: 768px) {
        [data-testid="stAppViewContainer"] > .main {
            padding: 2rem 1rem !important;
        }
    }
    
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Button styles */
    .stButton>button {
        width: 100% !important;
        justify-content: left !important;
        padding: 8px 16px !important;
    }

    /* Main content padding - applied globally */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    /* Ensure this stays in DOM during navigation */
    body {
        padding: 0 !important;
    }
    .st-emotion-cache-16txtl3 {
        padding: 1rem !important;
    }
    .stButton>button {
        width: 100% !important;
        justify-content: left !important;
        padding: 8px 16px !important;
    }
    /* Global padding for all pages */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with proper defaults
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False,
        "username": "",
        "preferences": [],
        "_last_page": "home",
        "_session_id": str(time.time()),
        "_pending_details": None
    })

# Custom sidebar menu
with st.sidebar:
    st.title("Menu")
    
    if st.session_state.logged_in:
        menu_choice = option_menu(
            menu_title=None,
            options=["Home", "Dashboard", "Logout"],
            icons=["house", "speedometer2", "box-arrow-right"],
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
            options=["Login", "Register"],
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

# Navigation handling
if menu_choice == "Home":
    st.session_state._last_page = "home"
    st.session_state._pending_details = None
    st.switch_page("pages/home.py")
elif menu_choice == "Dashboard":
    st.session_state._last_page = "dashboard"
    st.session_state._pending_details = None
    st.switch_page("pages/dashboard.py")
elif menu_choice == "Login":
    st.subheader("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.update({
                "logged_in": True,
                "username": username,
                "preferences": user["preferences"],
                "_session_id": str(time.time())
            })
            
            if st.session_state._pending_details:
                st.switch_page(f"pages/details.py?media_type={st.session_state._pending_details['media_type']}&id={st.session_state._pending_details['id']}")
            else:
                st.switch_page("pages/home.py")
elif menu_choice == "Register":
    st.subheader("Register New User")
    new_username = st.text_input("New Username", key="reg_username")
    new_password = st.text_input("New Password", type="password", key="reg_password")
    
    genres = ["Comedy", "Horror", "Sci-Fi", "Action", "Drama", "Romance"]
    preferences = st.multiselect(
        "Select Your Favorite Genres", 
        genres,
        key="reg_preferences"
    )

    if st.button("Register"):
        if not new_username or not new_password:
            st.error("Username and password are required")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters")
        elif not preferences:
            st.error("Please select at least one favorite genre")
        elif register_user(new_username, new_password, preferences):
            st.success("Registration successful! Please log in.")
        else:
            st.error("Username already exists")
elif menu_choice == "Logout":
    st.session_state.update({
        "logged_in": False,
        "username": "",
        "preferences": [],
        "_session_id": None,
        "_pending_details": None
    })
    # Clear the localStorage login state
    st.markdown("""
    <script>
    localStorage.removeItem('streamlit_login');
    localStorage.removeItem('streamlit_username');
    </script>
    """, unsafe_allow_html=True)
    # Redirect to login page
    st.switch_page("app.py")

# Add this at the BOTTOM of app.py for session persistence
if not st.session_state.logged_in and st.query_params.get("logged_in") == "True":
    st.session_state.logged_in = True
    st.session_state.username = st.query_params.get("username", "")
    st.rerun()

# Store login state in localStorage for persistence
st.markdown("""
<script>
if (window.location.search.includes('logged_in=True')) {
    localStorage.setItem('streamlit_login', 'true');
    localStorage.setItem('streamlit_username', '%s');
}
if (!window.location.search.includes('logged_in=True') && localStorage.getItem('streamlit_login') === 'true') {
    window.location.search = `?logged_in=True&username=${localStorage.getItem('streamlit_username')}`;
}
</script>
""" % st.session_state.username, unsafe_allow_html=True)