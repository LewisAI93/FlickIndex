import os
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Label, Button, ListView, ListItem
from textual.screen import Screen
from textual import on, work
from textual import events

from storage_module import (
    init_storage,
    load_data,
    add_to_favourites,
    add_to_watchlist,
    add_to_recently_viewed,
)

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

# =====================
# TEXTUAL APP INTERFACE
# =====================

class MovieScreen(Screen):
    def __init__(self, movie_data: dict):
        super().__init__()
        # store the dictionary passed from the search results for use in compose()
        self.movie_data = movie_data
        add_to_recently_viewed(self.movie_data)
        self.similar_movies = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="movie_details"):
                yield Label(f"Title: {self.movie_data.get('title')}")
                yield Label(f"Release Date: {self.movie_data.get('release_date')}")
                yield Label(f"Rating: {self.movie_data.get('vote_average')}")
                yield Label(" ")
                yield Label(self.movie_data.get("overview", "No overview available."))
                yield Label(" ")
                yield Button("Add to Favourites", id="fav_button", variant="success")
                yield Button("Add to Watchlist", id="watch_list_button", variant="primary")
                yield Button("Back to Search", id="back_button", variant="default")
            with Vertical(id="similar_pane"):
                yield Label("Similar Movies")
                yield ListView(id="similar_list")
        yield Footer()

    def on_mount(self) -> None:
        self.fetch_similar_movies_background()

    @work(thread=True)
    def fetch_similar_movies_background(self) -> None:
        try:
            movie_id = self.movie_data.get("id")
            if not movie_id:
                return
            similar = similar_movies(movie_id)
            self.similar_movies = similar
            self.app.call_from_thread(self.display_similar_movies, similar)
        except Exception as e:
            self.app.call_from_thread(self.display_similar_error, str(e))

    def display_similar_movies(self, movies: list) -> None:
        list_view = self.query_one("#similar_list", ListView)
        list_view.clear()

        if not movies:
            list_view.append(ListItem(Label("No similar movies found.")))
            return

        for movie in movies[:8]:
            title = movie.get("title", "Unknown")
            year = (movie.get("release_date") or "")[:4]
            label_text = f"{title} ({year})" if year else title
            list_view.append(
                ListItem(Label(label_text), id=f"similar_{movie.get('id')}")
            )

    def display_similar_error(self, error_msg: str) -> None:
        list_view = self.query_one("#similar_list", ListView)
        list_view.clear()
        list_view.append(ListItem(Label(f"Error loading similar movies: {error_msg}")))

    @on(ListView.Selected, "#similar_list")
    def open_similar_movie(self, event: ListView.Selected) -> None:
        if not event.item.id:
            return
        try:
            movie_id = int(event.item.id.split("_", 1)[1])
        except (IndexError, ValueError):
            return

        movie = next((m for m in self.similar_movies if m.get("id") == movie_id), None)
        if movie:
            self.app.push_screen(MovieScreen(movie))

    @on(Button.Pressed, "#back_button")
    def close_screen(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#fav_button")
    def save_favourite(self) -> None:
        add_to_favourites(self.movie_data)
        self.notify("Added to Favourites!")

    @on(Button.Pressed, "#watch_list_button")
    def save_watchlist(self) -> None:
        add_to_watchlist(self.movie_data)
        self.notify("Added to Watchlist!")

class ActorScreen(Screen):
    def __init__(self, actor_data: dict):
        super().__init__()
        self.actor_data = actor_data
        self.known_for_map = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="actor_details"):
            yield Label(f"Name: {self.actor_data.get('name')}")
            yield Label(f"Department: {self.actor_data.get('known_for_department')}")
            yield Label(f"Popularity: {self.actor_data.get('popularity')}")
            yield Label(" ")
            yield Label("Known For:")
            yield ListView(id="known_for_list")
            yield Label(" ")
            yield Button("Back to Search", id="back_button", variant="default")
        yield Footer()

    def on_mount(self) -> None:
        known_for_data = self.actor_data.get("known_for") or []
        list_view = self.query_one("#known_for_list", ListView)
        list_view.clear()
        self.known_for_map.clear()

        for item in known_for_data:
            title = item.get("title") or item.get("name") or "Unknown"
            year = (item.get("release_date") or item.get("first_air_date") or "")[:4]
            label_text = f"{title} ({year})" if year else title
            list_id = f"known_{item.get('id')}"
            self.known_for_map[list_id] = item
            list_view.append(ListItem(Label(label_text), id=list_id))

        if list_view.children:
            list_view.index = 0
            list_view.focus()

    @on(Button.Pressed, "#back_button")
    def close_screen(self) -> None:
        self.app.pop_screen()

    @on(ListView.Selected, "#known_for_list")
    def open_known_for(self, event: ListView.Selected) -> None:
        if not event.item.id:
            return
        movie = self.known_for_map.get(event.item.id)
        if not movie:
            return
        self.app.push_screen(MovieScreen(movie))

    def on_key(self, event: events.Key) -> None:
        if event.key == "space" and isinstance(self.focused, Button):
            self.focused.press()

class HomeScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal():
            with Vertical(id="left_pane"):
                yield Label("Search Database")
                yield Input(placeholder="Movie or Actor name...", id="search_input")
                yield Button("Search", id="search_button", variant="primary")
                yield ListView(id="results_list")
            
            with Vertical(id="right_pane"):
                yield Label("Recently Watched")
                yield ListView(id="recent_list")
                yield Button("View Watchlist", id="watchlist_button", variant="primary")
                yield Label("")
                yield Label("Your Favourites")
                yield ListView(id="favourites_list")
                yield Button("View Favourites", id="favourites_button", variant="primary")

        yield Footer()

    @on(Input.Submitted, "#search_input")
    @on(Button.Pressed, "#search_button")
    def execute_search(self) -> None:
        search_term = self.query_one("#search_input", Input).value
        results_list = self.query_one("#results_list", ListView)
        
        results_list.clear()

        if not search_term.strip():
            results_list.append(ListItem(Label("Error: Enter a search term.")))
            return
        
        results_list.append(ListItem(Label(f"Searching TMDB for '{search_term}'...")))
        self.fetch_search_results_background(search_term)

    # temp workaround before backend fix
    @work(thread=True)
    def fetch_search_results_background(self, query: str) -> None:
        """
        Runs the API calls on a background thread. 
        Without this, the app would freeze and stop responding while waiting 
         for TMDB to answer.
        """
        try:
            # Code here runs 'behind the scenes'
            movies = search_movies(query)
            actors = search_actor(query)
            
            combined_results = movies + actors
            combined_results.sort(key=lambda x: x.get("popularity") or 0, reverse=True)

            # We must use call_from_thread to send the data back to the 'Main Thread'
            # to safely update the UI widgets.
            self.app.call_from_thread(self.display_results, combined_results)
        except Exception as e:
            self.app.call_from_thread(self.display_error, str(e))

    current_results = {}

    def display_results(self, results: list) -> None:
        results_list = self.query_one("#results_list", ListView)
        results_list.clear()
        self.current_results.clear()
        
        if not results:
            results_list.append(ListItem(Label("No results found.")))
            return
            
        for item in results[:8]:
            item_id = str(item.get("id"))
            
            if "title" in item:
                title = item.get("title", "Unknown")
                year = (item.get("release_date") or "")[:4]
                label_text = f"{title} ({year})"
                list_id = f"movie_{item_id}"
            else:
                name = item.get("name", "Unknown")
                dept = item.get("known_for_department", "Unknown")
                label_text = f"{name} ({dept})"
                list_id = f"actor_{item_id}"
            
            self.current_results[list_id] = item
            results_list.append(ListItem(Label(label_text), id=list_id))
        
        # tabs to results
        results_list.focus()

    @on(ListView.Selected, "#results_list")
    def open_details(self, event: ListView.Selected) -> None:
        if not event.item.id:
            return
            
        selected_item = self.current_results.get(event.item.id)
        
        if not selected_item:
            return
            
        if event.item.id.startswith("movie_"):
            self.app.push_screen(MovieScreen(selected_item))
        elif event.item.id.startswith("actor_"):
            self.app.push_screen(ActorScreen(selected_item))

    def display_error(self, error_msg: str) -> None:
        results_list = self.query_one("#results_list", ListView)
        results_list.clear()
        results_list.append(ListItem(Label(f"API Error: {error_msg}")))

    def on_mount(self) -> None:
        """
        runs once automatically when the screen is first loaded
        """
        init_storage()
        self.refresh_side_panels()
    
    def on_screen_resume(self) -> None:
        """runs every time the user returns to this screen"""
        self.refresh_side_panels()
    
    def refresh_side_panels(self) -> None:
        """syncs the UI with current data in user_data.json"""
        stored_data = load_data()
        
        # update recently watched list
        recent_list = self.query_one("#recent_list", ListView)
        recent_list.clear()
        for movie in stored_data.get("recently_viewed", []):
            title = movie.get("title", "Unknown")
            recent_list.append(ListItem(Label(f"{title}")))

        # update favourites    
        favourites_list = self.query_one("#favourites_list", ListView)
        favourites_list.clear() 
        for movie in stored_data.get("favourites", []):
            title = movie.get("title", "Unknown")
            favourites_list.append(ListItem(Label(f"{title}")))


class FlickIndex(App):
    CSS = """
    #left_pane {
        width: 1fr;
        padding: 1;
    }
    #right_pane {
        width: 1fr;
        padding: 1;
        border-left: solid green;
    }
    """
    
    BINDINGS = [("q", "quit", "Quit application")]

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())
if __name__ == "__main__":
    app = FlickIndex()
    app.run()