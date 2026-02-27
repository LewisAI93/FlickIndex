import json
import os

# Constant for data file name
DATA_FILE = "user_data.json"


def init_storage():
    """
    Creates the JSON file if it does not exist.
    Prevents errors when loading data.
    """
    if not os.path.exists(DATA_FILE):
        data = {
            "favourites": [],
            "watchlist": [],
            "recently_viewed": []
        }

        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)


def load_data():
    """
    Loads data from JSON file and returns it as a dictionary.
    """
    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_data(data):
    """
    Saves the updated dictionary back into JSON file.
    """
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def add_to_watchlist(movie):
    """
    Add a movie dictionary to the watchlist.
    Prevent duplicates using movie ID.
    """
    data = load_data()

    for existing_movie in data["watchlist"]:
        if existing_movie["id"] == movie["id"]:
            print("Movie already in watchlist.")
            return

    data["watchlist"].append(movie)
    save_data(data)
    print("Movie added to watchlist.")


def remove_from_watchlist(movie_id):
    """
    Remove a movie from watchlist using its ID.
    """
    data = load_data()

    data["watchlist"] = [
        movie for movie in data["watchlist"]
        if movie["id"] != movie_id
    ]

    save_data(data)
    print("Movie removed from watchlist.")


def add_to_favourites(movie):
    """
    Add a movie to favourites.
    Prevent duplicates.
    """
    data = load_data()

    for existing_movie in data["favourites"]:
        if existing_movie["id"] == movie["id"]:
            print("Movie already in favourites.")
            return

    data["favourites"].append(movie)
    save_data(data)
    print("Movie added to favourites.")


def remove_from_favourites(movie_id):
    """
    Remove a movie from favourites using its ID.
    """
    data = load_data()

    data["favourites"] = [
        movie for movie in data["favourites"]
        if movie["id"] != movie_id
    ]

    save_data(data)
    print("Movie removed from favourites.")


def add_to_recently_viewed(movie):
    """
    Adds movie to recently viewed list.
    Keeps only last 10 items.
    """
    data = load_data()

    # Remove if already exists (so it moves to top)
    data["recently_viewed"] = [
        m for m in data["recently_viewed"]
        if m["id"] != movie["id"]
    ]

    # Insert at beginning
    data["recently_viewed"].insert(0, movie)

    # Keep only last 10
    data["recently_viewed"] = data["recently_viewed"][:10]

    save_data(data)