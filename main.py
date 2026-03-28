import os
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

# ==================
# TMDB API FUNCTIONS
# ==================

load_dotenv()

<<<<<<< HEAD
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")

=======
# Read the TMDB API key
# API key is required to authenticate requests to the TMDB API
# Store the API key in an environment variable for security
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")

# If there is no API key, return error message
>>>>>>> origin/main
if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY not set. Put it in .env")

def search_movies(query: str, *, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    """
<<<<<<< HEAD
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
=======
    Search for movies using TMDB API

    Parameters:
    - query: str (movie title or keyword)
    - language: str (language of the results)
    - page: int (page number of results)

    Returns
    - list (a list of movie dictionaries)
>>>>>>> origin/main
    """
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": language,
        "page": page,
    }

<<<<<<< HEAD
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
=======
    # Send a GET resquest to the TMDB API with the search parameters
    # Raise an error if request fails
    # Convert the JSON response into a Python dictionary
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Get the value associated with the key 'results' in the dictionary data
    # If 'results' doesn't exist, use an empty list
    results = data.get("results", [])

    # Create a simplified list of movie dictionaries
    # Extract relevant results using .get() so that missing fields don't crash the program
    simplified = []
    for item in results:
        vote = item.get("vote_average")
        if not vote or vote <= 1 or vote >= 9.9:
            continue
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

    # Rearrange the list in place
    # Highest popularity first, lowest popularity last
    # For each movie dictionary, get popularity value
    # If it is 'None', se 0 instead
    # Return the sorted list    
>>>>>>> origin/main
    simplified.sort(key=lambda p: p.get("popularity") or 0, reverse=True)
    return simplified

def search_actor(query: str, *, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    """
<<<<<<< HEAD
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
=======
    Search TMDB for people and returns a simplified, sorted list

    Parameters:
    - query: str (name of the person to search for)
    - language: str (language of the results)
    - page: int (page number of results)

    Returns:
    - list of dictionaries, each containing: 
        - id (id of the person from TMDB)
        - name (person's name)
        - known_for_department (department they are known for)
        - known_for (list of works they are known for)
        - popularity (popularity score)
>>>>>>> origin/main
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
<<<<<<< HEAD
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
=======
    Look for similar movies to a given movie on the TMDB API

    Parameters:
    - movie_id: int (id of the movie on TMDB)
    - language: str (language of the results)
    - page: int (page number of results)

    Returns:
    - a list of dictionaries containing movie information. The list is sorted by popularity in 
    descending order
>>>>>>> origin/main
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
<<<<<<< HEAD
=======
        vote = item.get("vote_average")
        if not vote or vote <= 1 or vote >= 9.9:
            continue
>>>>>>> origin/main
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
<<<<<<< HEAD
    return simplified
=======
    return simplified

def genres_list(*, language: str = "en-US") -> List[Dict[str, Any]]:
    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return data.get("genres", [])

def search_genre(genre_id: int, *, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
        "page": page,
        "with_genres": genre_id,
        "sort_by": "popularity.desc",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])

    simplified = []
    for item in results:
        vote = item.get("vote_average")
        if not vote or vote <= 1 or vote >= 9.9:
            continue
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

def popular_movies(*, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    url = f"{TMDB_BASE_URL}/movie/popular"
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
        vote = item.get("vote_average")
        if not vote or vote <= 1 or vote >= 9.9:
            continue
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
>>>>>>> origin/main
