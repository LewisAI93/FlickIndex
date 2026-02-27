import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search_person(name: str):
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        print("Error: TMDB_API_KEY is not set.")
        return []

    url = "https://api.themoviedb.org/3/search/person"
    params = {"api_key": api_key, "query": name}
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("results", [])

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
    return search_person(actor)

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

def search_by_director(director: str):
    people = search_person(director)
    if not people:
        return []

    person_id = people[0].get("id")
    if person_id is None:
        return []


    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        print("Error: TMDB_API_KEY is not set.")
        return []

    url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits"
    params = {"api_key": api_key}
    data = requests.get(url, params=params).json()
    crew = data.get("crew", [])
    directed = [c for c in crew if c.get("job") == "Director"]
    return directed

###WIP### Lewis
def search_by_genre(genre: str):
    genre = search_by_genre(genre)
    # api_key = os.environ.get("TMDB_API_KEY")
    # if not api_key:
    #     print("Error: TMDB_API_KEY is not set.")
    #     return []
    # url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar"
    # params = {
    #     "api_key": api_key,
    #     "language": "en-US",
    #     "page": 1
    # }
    # response = requests.get(url, params=params)
    # data = response.json()
    # results = data.get("results", [])
    # return results