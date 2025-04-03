import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"
    
    def get_item_details(self, media_type, item_id):
        url = f"{self.base_url}/{media_type}/{item_id}"
        params = {"api_key": self.api_key}
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None
    
    def get_genre_mapping(self, media_type):
        url = f"{self.base_url}/genre/{media_type}/list"
        response = requests.get(url, params={"api_key": self.api_key})
        if response.status_code == 200:
            return {g['id']: g['name'] for g in response.json().get('genres', [])}
        return {}