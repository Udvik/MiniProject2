import streamlit as st

# Redirect to login if not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("You need to log in first!")
    st.stop()  # Stops execution here

# Home Page Content
st.title("Welcome to the Movie Recommendation System 🎬")
st.write(f"Hello, {st.session_state['username']}!")

if "preferences" in st.session_state:
    st.write("Your selected genres:", ", ".join(st.session_state["preferences"]))

st.write("Movie recommendations will be displayed here based on your preferences!")
