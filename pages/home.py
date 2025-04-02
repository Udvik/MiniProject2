import streamlit as st
import requests
import os
from db import add_watched_content, add_liked_content, get_friends, get_user_content

# Add this at the top of home.py (right after imports)
st.markdown("""
<style>
    /* Main content padding */
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
    
    .stCaption {
        font-size: 14px !important;
        text-align: center !important;
        margin-top: 8px !important;
    }
    img:hover {
        opacity: 0.9;
        transition: opacity 0.2s;
        cursor: pointer;
    }
    
    /* New styles for watched/liked buttons */
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
    }
    .action-btn {
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        cursor: pointer;
        border: none;
        transition: all 0.3s;
    }
    .action-btn:hover {
        transform: translateY(-2px);
    }
    .watched-btn {
        background-color: #4CAF50;
        color: white;
    }
    .liked-btn {
        background-color: #f44336;
        color: white;
    }
    
    /* Poster container styles */
    .poster-container {
        position: relative;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

def get_friends_activity(username, limit=8):
    """Get recently watched items from friends"""
    friends = get_friends(username)
    all_watched = []
    
    for friend in friends:
        friend_content = get_user_content(friend)
        for item in friend_content.get("watched", []):
            item["friend_username"] = friend
            all_watched.append(item)
    
    # Sort by date added (newest first)
    all_watched.sort(key=lambda x: x.get("added_at", ""), reverse=True)
    return all_watched[:limit]

def get_popular_with_friends(username):
    """Get items most frequently watched by friends with high ratings"""
    friends = get_friends(username)
    content_counts = {}
    
    for friend in friends:
        friend_content = get_user_content(friend)
        for item in friend_content.get("watched", []):
            key = (item["type"], item["id"], item["title"])
            if key not in content_counts:
                content_counts[key] = {
                    "count": 0,
                    "friend_usernames": []
                }
            content_counts[key]["count"] += 1
            content_counts[key]["friend_usernames"].append(friend)
    
    # Sort by watch count (descending)
    sorted_items = sorted(content_counts.items(), key=lambda x: x[1]["count"], reverse=True)
    
    # Convert to list of items with metadata
    result = []
    for (media_type, item_id, title), data in sorted_items[:8]:
        result.append({
            "type": media_type,
            "id": item_id,
            "title": title,
            "watch_count": data["count"],
            "friends": data["friend_usernames"]
        })
    
    return result

def display_content(items, media_type, caption_field="title"):
    cols = st.columns(4)
    for i, item in enumerate(items[:8]):
        with cols[i % 4]:
            poster_path = item.get("poster_path")
            title = (item.get("title") or item.get("name"))[:20] + "..." if len(item.get("title") or item.get("name")) > 20 else (item.get("title") or item.get("name"))
            item_id = item.get("id")
            
            if poster_path and item_id:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                details_url = f"/details?media_type={media_type}&id={item_id}"
                st.markdown(
                    f'''
                    <div class="poster-container">
                        <a href="{details_url}" target="_blank">
                            <img src="{poster_url}" 
                                 style="width:100%; height:auto; aspect-ratio:2/3; object-fit:cover; border-radius:8px;"
                                 alt="{title}">
                        </a>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            else:
                # Placeholder matching poster aspect ratio
                st.markdown(
                    '<div style="width:100%; aspect-ratio:2/3; background:#eee; border-radius:8px; display:flex; '
                    'align-items:center; justify-content:center; margin-bottom:8px;">'
                    '<span style="color:#666;">No Image</span></div>',
                    unsafe_allow_html=True
                )
            
            # Add Watched/Liked buttons below each item
            if st.session_state.get("logged_in", False):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅", key=f"watched_{item_id}_{i}"):
                        add_watched_content(
                            st.session_state.username,
                            media_type,
                            item_id,
                            title
                        )
                        st.success(f"Added {title} to watched list!")
                with col2:
                    if st.button("❤️", key=f"liked_{item_id}_{i}"):
                        add_liked_content(
                            st.session_state.username,
                            media_type,
                            item_id,
                            title
                        )
                        st.success(f"Added {title} to liked list!")
            
            st.caption(item.get(caption_field, title))

def fetch_poster(media_type, item_id):
    API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    response = requests.get(url, params={"api_key": API_KEY})
    if response.status_code == 200:
        return response.json().get("poster_path")
    return None

def fetch_popular_movies():
    API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}"
    response = requests.get(url)
    return response.json().get("results", []) if response.status_code == 200 else []

def fetch_popular_tv():
    API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}"
    response = requests.get(url)
    return response.json().get("results", []) if response.status_code == 200 else []

def search_content(query):
    API_KEY = os.getenv("TMDB_API_KEY")
    url = "https://api.themoviedb.org/3/search/multi"
    params = {"api_key": API_KEY, "query": query}
    response = requests.get(url, params=params)
    return response.json().get("results", []) if response.status_code == 200 else []

# --- Streamlit UI Code ---
st.title("🎬 Entertainment Explorer")

query = st.text_input("🔍 Search for movies or TV shows...")

if query:
    results = search_content(query)
    movies = [r for r in results if r.get("media_type") == "movie"]
    tv_shows = [r for r in results if r.get("media_type") == "tv"]
    
    if movies:
        st.subheader("Movies")
        display_content(movies, "movie")
    
    if tv_shows:
        st.subheader("TV Shows")
        display_content(tv_shows, "tv")
else:
    st.subheader("Popular Movies")
    movies = fetch_popular_movies()
    display_content(movies, "movie")
    
    st.subheader("Popular TV Shows")
    tv_shows = fetch_popular_tv()
    display_content(tv_shows, "tv")

    # New Friends Activity Sections (only shown when logged in)
    if st.session_state.get("logged_in", False):
        # New from Friends section
        st.subheader("New from Friends")
        friends_activity = get_friends_activity(st.session_state.username)
        
        if friends_activity:
            # Enhance items with poster paths
            for item in friends_activity:
                item["poster_path"] = fetch_poster(item["type"], item["id"])
            
            cols = st.columns(4)
            for idx, item in enumerate(friends_activity[:8]):
                with cols[idx % 4]:
                    poster_path = item.get("poster_path")
                    details_url = f"/details?media_type={item['type']}&id={item['id']}"
                    
                    if poster_path:
                        st.markdown(
                            f'<div class="poster-container">'
                            f'<a href="{details_url}" target="_blank">'
                            f'<img src="https://image.tmdb.org/t/p/w500{poster_path}" '
                            f'style="width:100%; height:auto; aspect-ratio:2/3; object-fit:cover; border-radius:8px;">'
                            f'</a>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div style="width:100%; aspect-ratio:2/3; background:#eee; border-radius:8px; display:flex; '
                            'align-items:center; justify-content:center; margin-bottom:8px;">'
                            '<span style="color:#666;">No Image</span></div>',
                            unsafe_allow_html=True
                        )
                    
                    st.caption(f"Watched by {item['friend_username']}")
        else:
            st.info("Your friends haven't watched anything yet")

        # Popular with Friends section
        st.subheader("Popular with Friends")
        popular_with_friends = get_popular_with_friends(st.session_state.username)
        
        if popular_with_friends:
            # Enhance items with poster paths
            for item in popular_with_friends:
                item["poster_path"] = fetch_poster(item["type"], item["id"])
                item["friends_count"] = f"{item['watch_count']} friends watched"
            
            cols = st.columns(4)
            for idx, item in enumerate(popular_with_friends[:8]):
                with cols[idx % 4]:
                    poster_path = item.get("poster_path")
                    details_url = f"/details?media_type={item['type']}&id={item['id']}"
                    
                    if poster_path:
                        st.markdown(
                            f'<div class="poster-container">'
                            f'<a href="{details_url}" target="_blank">'
                            f'<img src="https://image.tmdb.org/t/p/w500{poster_path}" '
                            f'style="width:100%; height:auto; aspect-ratio:2/3; object-fit:cover; border-radius:8px;">'
                            f'</a>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div style="width:100%; aspect-ratio:2/3; background:#eee; border-radius:8px; display:flex; '
                            'align-items:center; justify-content:center; margin-bottom:8px;">'
                            '<span style="color:#666;">No Image</span></div>',
                            unsafe_allow_html=True
                        )
                    
                    st.caption(f"{item['title']} ({item['friends_count']})")
        else:
            st.info("No popular content among your friends yet")