import json
import os

# Constant for data file name
DATA_FILE = "user_data.json"

# Cached in-memory storage
data_cache = None


def init_storage():
    """
    Creates the JSON file if it does not exist.
    Loads the data into memory cache.
    """
    global data_cache

    if not os.path.exists(DATA_FILE):
        data_cache = {
            "favourites": [],
            "watchlist": [],
            "recently_viewed": []
        }

        with open(DATA_FILE, "w") as file:
            json.dump(data_cache, file, indent=4)

    else:
        with open(DATA_FILE, "r") as file:
            data_cache = json.load(file)


def load_data():
    """
    Returns cached data instead of reading file every time.
    """
    global data_cache

    if data_cache is None:
        with open(DATA_FILE, "r") as file:
            data_cache = json.load(file)

    return data_cache


def save_data():
    """
    Saves cached data to JSON file.
    """
    global data_cache

    with open(DATA_FILE, "w") as file:
        json.dump(data_cache, file, indent=4)


def add_to_watchlist(movie):
    """
    Add a movie dictionary to the watchlist.
    Prevent duplicates using movie ID.
    """
    data = load_data()

    for existing_movie in data["watchlist"]:
        if existing_movie["id"] == movie["id"]:
            return False

    data["watchlist"].append(movie)

    save_data()

    return True


def remove_from_watchlist(movie_id):
    """
    Remove a movie from watchlist using its ID.
    """
    data = load_data()

    original_length = len(data["watchlist"])

    data["watchlist"] = [
        movie for movie in data["watchlist"]
        if movie["id"] != movie_id
    ]

    if len(data["watchlist"]) == original_length:
        return False

    save_data()

    return True


def add_to_favourites(movie):
    """
    Add a movie to favourites.
    Prevent duplicates.
    """
    data = load_data()

    for existing_movie in data["favourites"]:
        if existing_movie["id"] == movie["id"]:
            return False

    data["favourites"].append(movie)

    save_data()

    return True


def remove_from_favourites(movie_id):
    """
    Remove a movie from favourites using its ID.
    """
    data = load_data()

    original_length = len(data["favourites"])

    data["favourites"] = [
        movie for movie in data["favourites"]
        if movie["id"] != movie_id
    ]

    if len(data["favourites"]) == original_length:
        return False

    save_data()

    return True


def add_to_recently_viewed(movie):
    """
    Adds movie to recently viewed list.
    Keeps only last 10 items.
    """
    data = load_data()

    # Remove if already exists
    data["recently_viewed"] = [
        m for m in data["recently_viewed"]
        if m["id"] != movie["id"]
    ]

    # Insert at beginning
    data["recently_viewed"].insert(0, movie)

    # Keep only last 10
    data["recently_viewed"] = data["recently_viewed"][:10]

    save_data()

    return True

def is_favourite(movie_id):
    """Checks if a movie ID exists in favourites."""
    data = load_data()
    return any(movie["id"] == movie_id for movie in data["favourites"])

def is_in_watchlist(movie_id):
    """Checks if a movie ID exists in the watchlist."""
    data = load_data()
    return any(movie["id"] == movie_id for movie in data["watchlist"])