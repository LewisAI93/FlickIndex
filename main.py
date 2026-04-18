import os
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

# ==================
# TMDB API FUNCTIONS
# ==================

load_dotenv()

# Read the TMDB API key
# API key is required to authenticate requests to the TMDB API
# Store the API key in an environment variable for security
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")

# If there is no API key, return error message
if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY not set. Put it in .env")

def search_movies(query: str, *, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    """
    Search for movies using TMDB API

    Parameters:
    - query: str (movie title or keyword)
    - language: str (language of the results)
    - page: int (page number of results)

    Returns
    - list (a list of movie dictionaries)
    """
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": language,
        "page": page,
    }

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
    simplified.sort(key=lambda p: p.get("popularity") or 0, reverse=True)
    return simplified

def search_actor(query: str, *, language: str = "en-US", page: int = 1) -> List[Dict[str, Any]]:
    """
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
    Look for similar movies to a given movie on the TMDB API

    Parameters:
    - movie_id: int (id of the movie on TMDB)
    - language: str (language of the results)
    - page: int (page number of results)

    Returns:
    - a list of dictionaries containing movie information. The list is sorted by popularity in 
    descending order
    """
    details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    details_params = {
        "api_key": TMDB_API_KEY,
        "language": language,
    }
    details_resp = requests.get(details_url, params=details_params, timeout=10)
    details_resp.raise_for_status()
    details = details_resp.json()

    similar: List[Dict[str, Any]] = []

    collection = details.get("belongs_to_collection")
    if collection:
        collection_id = collection.get("id")
        if collection_id:
            collection_url = f"{TMDB_BASE_URL}/collection/{collection_id}"
            collection_params = {
                "api_key": TMDB_API_KEY,
                "language": language,
            }
            col_resp = requests.get(collection_url, params=collection_params, timeout=10)
            col_resp.raise_for_status()
            col_data = col_resp.json()
            parts = col_data.get("parts", [])

            parts.sort(key=lambda p: (p.get("release_date") or "9999-99-99"))

            for item in parts:
                if item.get("id") == movie_id:
                    continue
                vote = item.get("vote_average")
                if not vote or vote <= 1 or vote >= 9.9:
                    continue
                similar.append(
                    {
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "release_date": item.get("release_date"),
                        "overview": item.get("overview"),
                        "vote_average": item.get("vote_average"),
                        "popularity": item.get("popularity"),
                    }
                )

    if len(similar) < 10:
        rec_url = f"{TMDB_BASE_URL}/movie/{movie_id}/recommendations"
        rec_params = {
            "api_key": TMDB_API_KEY,
            "language": language,
            "page": page,
        }
        rec_resp = requests.get(rec_url, params=rec_params, timeout=10)
        rec_resp.raise_for_status()
        rec_data = rec_resp.json()
        rec_results = rec_data.get("results", [])

        existing_ids = {m["id"] for m in similar}
        for item in rec_results:
            mid = item.get("id")
            if not mid or mid in existing_ids or mid == movie_id:
                continue
            vote = item.get("vote_average")
            if not vote or vote <= 1 or vote >= 9.9:
                continue
            similar.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "release_date": item.get("release_date"),
                    "overview": item.get("overview"),
                    "vote_average": item.get("vote_average"),
                    "popularity": item.get("popularity"),
                }
            )
            existing_ids.add(mid)

    similar.sort(key=lambda p: p.get("popularity") or 0, reverse=True)
    return similar

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