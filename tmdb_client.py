import os
import requests

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