
import streamlit as st

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("You need to log in first!")
    st.stop() 
st.title("DashBoard Page")