from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Label, Button, ListView, ListItem
from textual.screen import Screen
from textual import on, work, events

from main import search_movies, search_actor, similar_movies
from storage_module import (
    init_storage,
    load_data,
    add_to_favourites,
    add_to_watchlist,
    add_to_recently_viewed,
)

# ===============
# ASCII art 4 fun
# ===============

ASCII_WATCHLIST = r"""
.::        .::            .::                  .::            .::  
.::        .::            .::         .::      .:: .:         .::  
.::   .:   .::   .::    .:.: .:   .:::.::      .::    .:::: .:.: .:
.::  .::   .:: .::  .::   .::   .::   .: .:    .::.::.::      .::  
.:: .: .:: .::.::   .::   .::  .::    .::  .:: .::.::  .:::   .::  
.: .:    .::::.::   .::   .::   .::   .:   .:: .::.::    .::  .::  
.::        .::  .:: .:::   .::    .:::.::  .::.:::.::.:: .::   .:: 
"""

ASCII_FAVOURITES = r"""
.::::::::                                                   .::                   
.::                                                     .:  .::                   
.::         .::    .::     .::   .::    .::  .::.: .:::   .:.: .:   .::     .:::: 
.::::::   .::  .::  .::   .::  .::  .:: .::  .:: .::   .::  .::   .:   .:: .::    
.::      .::   .::   .:: .::  .::    .::.::  .:: .::   .::  .::  .::::: .::  .::: 
.::      .::   .::    .:.::    .::  .:: .::  .:: .::   .::  .::  .:            .::
.::        .:: .:::    .::       .::      .::.::.:::   .::   .::   .::::   .:: .::
"""

# =====================
# TEXTUAL APP INTERFACE
# =====================

class HomeScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal():
            with Vertical(id="left_pane"):
                yield Label("Search Database", classes="section_heading")
                yield Input(placeholder="Movie or Actor name...", id="search_input")
                yield Button("Search", id="search_button", variant="primary")
                yield ListView(id="results_list")

                yield Label("Recently Viewed", classes="section_heading")
                yield ListView(id="recent_list")

                yield Label(" ")
                yield Button("Quit Application", id="quit_button", variant="error")
            
            with Vertical(id="right_pane"):
                yield Label("Your Favourites", classes="section_heading")
                yield ListView(id="favourites_list")
                yield Button("View Favourites", id="favourites_button", variant="primary")
                
                yield Label("Your Watchlist", classes="section_heading")
                yield ListView(id="watchlist_preview_list")
                yield Button("View Watchlist", id="watchlist_button", variant="primary")


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

    @work(thread=True)
    def fetch_search_results_background(self, query: str) -> None:
        try:
            movies = search_movies(query)
            actors = search_actor(query)
            
            combined_results = movies + actors
            combined_results.sort(key=lambda x: x.get("popularity") or 0, reverse=True)

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
        init_storage()
        self.refresh_side_panels()
    
    def on_screen_resume(self) -> None:
        self.refresh_side_panels()
    
    def refresh_side_panels(self) -> None:
        stored_data = load_data()
        
        recent_list = self.query_one("#recent_list", ListView)
        recent_list.clear()
        for movie in stored_data.get("recently_viewed", []):
            title = movie.get("title", "Unknown")
            recent_list.append(ListItem(Label(f"{title}")))

        favourites_list = self.query_one("#favourites_list", ListView)
        favourites_list.clear() 
        for movie in stored_data.get("favourites", []):
            title = movie.get("title", "Unknown")
            favourites_list.append(ListItem(Label(f"{title}")))

        watchlist_list = self.query_one("#watchlist_preview_list", ListView)
        watchlist_list.clear() 
        for movie in stored_data.get("watchlist", []):
            title = movie.get("title", "Unknown")
            watchlist_list.append(ListItem(Label(f"{title}")))    
            
    @on(Button.Pressed, "#watchlist_button")
    def view_watchlist(self) -> None:
        data = load_data()
        watchlist = data.get("watchlist", [])
        self.app.push_screen(CollectionScreen(ASCII_WATCHLIST, watchlist, "watchlist"))

    @on(Button.Pressed, "#favourites_button")
    def view_favourites(self) -> None:
        data = load_data()
        favourites = data.get("favourites", [])
        self.app.push_screen(CollectionScreen(ASCII_FAVOURITES, favourites, "favourites"))

    @on(Button.Pressed, "#quit_button")
    def action_quit_app(self) -> None:
        """Exit application action"""
        self.app.exit()


class MovieScreen(Screen):
    def __init__(self, movie_data: dict):
        super().__init__()
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
                yield Button("Back", id="back_button", variant="default")
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

class CollectionScreen(Screen):
    """
    A reusable screen to display specific collections - Favourites, Watchlist
    """
    # Bind the 'd' key to the action_remove_item method
    BINDINGS = [("d", "remove_item", "Delete Selected")]
    
    def __init__(self, title: str, movie_list: list, collection_type: str):
        super().__init__()
        self.display_title = title
        self.movies = movie_list
        self.collection_type = collection_type # e.g. favourites or watchlist
        self.movie_map = {} # Cache to map UI IDs to data

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="collection_container"):
            yield Label(self.display_title, id="ascii_header")
            
            # Buttons moved ABOVE the list to fix notification overlap
            with Horizontal(id="collection_actions"):
                yield Button("Back to Home", id="back_to_home", variant="default")
                yield Button("Remove Selected", id="remove_selected", variant="error")
                
            yield ListView(id="collection_list")
        yield Footer()
    
    def on_mount(self) -> None:
        list_view = self.query_one("#collection_list", ListView)
        list_view.clear()

        if not self.movies:
            list_view.append(ListItem(Label("List is currently empty.")))
            return
        
        for movie in self.movies:
            title = movie.get("title", "Unknown")
            year = (movie.get("release_date") or "")[:4]
            label_text = f"{title} ({year})" if year else title
            list_id = f"coll_{movie.get('id')}"

            self.movie_map[list_id] = movie
            list_view.append(ListItem(Label(label_text), id=list_id))

        list_view.focus()

    @on(ListView.Selected, "#collection_list")
    def open_movie_detail(self, event: ListView.Selected) -> None:
        movie = self.movie_map.get(event.item.id)
        if movie:
            self.app.push_screen(MovieScreen(movie))

    @on(Button.Pressed, "#back_to_home")
    def close_screen(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#remove_selected")
    def remove_item(self) -> None:
        list_view = self.query_one("#collection_list", ListView)
        selected_item = list_view.highlighted_child
        
        if not selected_item:
            self.notify("Error: No item selected.")
            return

        movie = self.movie_map.get(selected_item.id)
        if not movie:
            return

        selected_item.remove()
        title = movie.get('title', 'Unknown')

        if self.collection_type == "favourites":
            # TODO: remove_from_favourites(movie) 
            self.notify(f"Removed '{title}' from Favourites.")
        elif self.collection_type == "watchlist":
            # TODO: remove_from_watchlist(movie)
            self.notify(f"Removed '{title}' from Watchlist.")

class FlickIndex(App):
    CSS = """
    #left_pane {
        width: 1fr;
        padding: 2;
    }
    #right_pane {
        width: 1fr;
        padding: 2;
        border-left: solid green;
    }
    
    #collection_header {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        background: $primary;
        color: $text;
        margin-bottom: 2;
        padding: 1;
        border: tall $secondary;
    }

    #ascii_header {
        text-align: center;
        width: 100%;
        height: auto;
        color: $primary;
        margin-bottom: 1;
    }

    #collection_actions {
        height: auto;
        margin-top: 1;
        align: center middle;
    }
    
    #collection_actions Button {
        margin: 0 1;
    }

    .section_heading {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 1;
        border-bottom: solid $secondary;
        width: 100%;
    }
    """

    
    BINDINGS = [("q", "quit", "Quit application")]

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())

if __name__ == "__main__":
    app = FlickIndex()
    app.run()