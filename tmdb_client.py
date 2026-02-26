import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search_by_title(title: str):
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        print("Error: TMDB_API_KEY is not set.")
        return []
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": title
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = data.get("results", [])
    return results

def search_by_actor(actor: str):
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        print("Error: TMDB_API_KEY is not set.")
        return []
    url = "https://api.themoviedb.org/3/search/person"
    params = {
        "api_key": api_key,
        "query": actor
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = data.get("results", [])
    return results

def search_related_movies(movie_id: int):
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        print("Error: TMDB_API_KEY is not set.")
        return []
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar"
    params = {
        "api_key": api_key,
        "language": "en-US",
        "page": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = data.get("results", [])
    return results

