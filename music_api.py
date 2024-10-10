import requests
import pandas as pd

class MusicAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.jamendo.com/v3.0/tracks/"

    def search_instrumental_music(self, tags="instrumental"):
        params = {
            "client_id": self.api_key,
            "format": "json",
            "limit": 200,
            "tags": tags,
            "include": "musicinfo",
            "f_haslyrics": False,
            "order": "popularity_total"
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json().get("results", [])
            data = pd.DataFrame(data)
            return data
        else:
            raise Exception(f"API Error: {response.status_code}")
