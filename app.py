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
    
    /* Default button styles */
    .stButton>button {
        width: 100% !important;
        padding: 8px 16px !important;
    }

    /* Special class for centered buttons */
    .centered-button .stButton>button {
        display: flex;
        justify-content: center;
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
     /* ===== OVERRIDE STREAMLIT'S MOBILE DEFAULTS ===== */
    /* Disable automatic column stacking */
    @media (max-width: 768px) {
        .stHorizontal > div {
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
        }
        
        /* Force 4-column grid */
        .poster-grid-container {
            display: grid !important;
            grid-template-columns: repeat(4, minmax(60px, 1fr)) !important;
            gap: 8px !important;
            width: 100% !important;
        }
        
        /* Prevent container padding from shrinking grid */
        [data-testid="stAppViewContainer"] > .main {
            padding: 1rem 0.5rem !important;
            min-width: 280px !important; /* Minimum for 4x60px + gaps */
        }
        
        /* Poster sizing */
        .poster-item {
            width: 22vw !important;
            min-width: 60px !important;
            max-width: 80px !important;
        }
    }
    
    /* ===== DESKTOP ENHANCEMENTS ===== */
    @media (min-width: 769px) {
        .poster-grid-container {
            grid-template-columns: repeat(4, minmax(120px, 1fr)) !important;
            gap: 12px !important;
        }
        .poster-item {
            max-width: 150px !important;
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
        "_pending_details": None,
        "_current_friend": None
    })

# Custom sidebar menu
with st.sidebar:
    st.title("Menu")
    
    if st.session_state.logged_in:
        menu_options = ["Home", "Dashboard", "Friends", "Recommendations", "Logout"]
        menu_icons = ["house", "speedometer2", "people", "chat-square-heart", "box-arrow-right"]
        
        menu_choice = option_menu(
            menu_title=None,
            options=menu_options,
            icons=menu_icons,
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
elif menu_choice == "Friends":
    st.session_state._last_page = "friends"
    st.session_state._pending_details = None
    st.switch_page("pages/friends.py")
elif menu_choice == "Recommendations":
    st.session_state._last_page = "recommendations"
    st.session_state._pending_details = None
    st.switch_page("pages/recommendations.py")
elif menu_choice == "Login":
    st.subheader("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Create a container with our centered-button class
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
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

    # Create a container with our centered-button class
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
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
        "_pending_details": None,
        "_current_friend": None
    })
    st.markdown("""
    <script>
    localStorage.removeItem('streamlit_login');
    localStorage.removeItem('streamlit_username');
    </script>
    """, unsafe_allow_html=True)
    st.switch_page("app.py")

# Session persistence code
if not st.session_state.logged_in and st.query_params.get("logged_in") == "True":
    st.session_state.logged_in = True
    st.session_state.username = st.query_params.get("username", "")
    st.rerun()

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