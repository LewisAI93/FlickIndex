from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Label, Button, ListView, ListItem
from textual.screen import Screen
from textual import on, work

from main import search_movies,search_actor
from storage_module import init_storage, load_data, add_to_favourites, add_to_watchlist

class MovieScreen(Screen):
    def __init__(self, movie_data: dict):
        super().__init__()
        # store the dictionary passed from the search results for use in compose()
        self.movie_data = movie_data

    def compose(self) -> ComposeResult:
        yield Header()
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
        yield Footer()

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

    def compose(self) -> ComposeResult:
        known_for_data = self.actor_data.get("known_for") or []
        titles = [item.get("title") or item.get("name") for item in known_for_data]
        known_for_str = ", ".join([t for t in titles if t]) if titles else "No known works."

        yield Header()
        with Vertical(id="actor_details"):
            yield Label(f"Name: {self.actor_data.get('name')}")
            yield Label(f"Department: {self.actor_data.get('known_for_department')}")
            yield Label(f"Popularity: {self.actor_data.get('popularity')}")
            yield Label(" ")
            yield Label(f"Known For: {known_for_str}")
            yield Label(" ")
            yield Button("Back to Search", id="back_button", variant="default")
        yield Footer()

    @on(Button.Pressed, "#back_button")
    def close_screen(self) -> None:
        self.app.pop_screen()

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
        on_mount runs automatically when the screen is first loaded.
        Used to load initial data from files or set the starting focus.
        """
        init_storage()
        
        stored_data = load_data()
        
        recent_list = self.query_one("#recent_list", ListView)
        for movie in stored_data.get("recently_viewed", []):
            title = movie.get("title", "Unknown")
            recent_list.append(ListItem(Label(f"{title}")))
            
        favourites_list = self.query_one("#favourites_list", ListView)
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