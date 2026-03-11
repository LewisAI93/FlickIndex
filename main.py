import os
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

# ==================
# TMDB API FUNCTIONS
# ==================

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")

if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY not set. Put it in .env")

def search_movies(query: str, *, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    """
    Search for movies using the TMDB API and return data about the movie

    Args:
    - query (str): the search query string (ex. movie)
    - language (str): set to English by default
    - page (int): page number for results. Starts on page 1

    Returns:
        List[Dic[str, Any]]: returns a dictionary containing:
        - id (int): numerical id of the movie on the TMDB API
        - title (str): title of the movie
        - overview (str): brief overview of the movie
        - vote average (float): average rating of the movie
        - popularity (float): popularity score
    """
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": language,
        "page": page,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])

    simplified = []
    for item in results:
        simplified.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "release_date": item.get("release_date"),
                "overview": item.get("overview"),
                "vote_average": item.get("vote_average"),
                "popularity": item.get("popularity"),
            }
        )
    simplified.sort(key=lambda p: p.get("popularity") or 0, reverse=True)
    return simplified

def search_actor(query: str, *, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    """
    Search for actors using the TMDB API and return data about the actor

    Args:
    - query (str): query of actor's name
    - language (str): set to English by default
    - page (int): page number for results. Starts on page 1

    Returns:
        List[Dict[str, any]]: a dictionary containing:
        - id (int): numerical ID of the actor on TMDB API
        - name (str): name of the actor
        - known for department (str): genres that the actor is known for
        - known for (str): movies that the actor is known for
        - popularity (float): popularity score
    """
    url = f"{TMDB_BASE_URL}/search/person"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": language,
        "page": page,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])

    simplified = []
    for item in results:
        simplified.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "known_for_department": item.get("known_for_department"),
                "known_for": item.get("known_for"),
                "popularity": item.get("popularity"),
            }
        )
    simplified.sort(key=lambda p: p.get("popularity") or 0, reverse=True)
    return simplified

def similar_movies(movie_id: int, *, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    """
    Search for similar movies on the TMDB API and return data about the movies

    Args: 
    - movie id (int): numerical id of the movie on the TMDB API
    - language (str): set to English by default
    - page (int): page number for results. Starts at 1

    Returns:
        List[Dict[str, Any]]: a dictionary containing:
        - id (int): numerical id of the movie on the TMDB API
        - title (str): title of the movie
        - release date (int): when the movie was released
        - vote average (float): average rating of the movie
        - popularity (float): popularity score
    """
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/similar"
    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
        "page": page,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])

    simplified = []
    for item in results:
        simplified.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "release_date": item.get("release_date"),
                "overview": item.get("overview"),
                "vote_average": item.get("vote_average"),
                "popularity": item.get("popularity"),
            }
        )
    simplified.sort(key=lambda p: p.get("popularity") or 0, reverse=True)
    return simplified