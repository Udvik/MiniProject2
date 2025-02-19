import streamlit as st
from db import register_user, login_user

# Session state to track login status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

st.title("User Authentication System")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login":
    st.subheader("Login Page")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if login_user(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or password")

elif choice == "Register":
    st.subheader("Register New User")
    
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    
    if st.button("Register"):
        if register_user(new_username, new_password):
            st.success("Registration successful! Please log in.")
        else:
            st.error("Username already exists. Try a different one.")

# Logout Button
if st.session_state["logged_in"]:
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.success("Logged out successfully!")
