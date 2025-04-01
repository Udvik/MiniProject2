# utils/content_grid.py
import streamlit as st
import requests
import os

def display_content_grid(items, media_type, cols=4):
    columns = st.columns(cols)
    for idx, item in enumerate(items):
        with columns[idx % cols]:
            poster_path = item.get("poster_path")
            title = (item.get("title") or item.get("name"))[:20] + "..." 
            item_id = item.get("id")
            
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                details_url = f"/details?media_type={media_type}&id={item_id}"
                st.markdown(
                    f'<a href="{details_url}" target="_blank">'
                    f'<img src="{poster_url}" style="width:100%; border-radius:8px;">'
                    '</a>',
                    unsafe_allow_html=True
                )
            else:
                st.image("https://via.placeholder.com/150x225?text=No+Poster")
            
            st.caption(title)
            
            if st.session_state.get("logged_in", False):
                # Add watched/liked buttons
                pass