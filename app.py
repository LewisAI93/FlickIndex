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
        """
        Defines the UI layout in terminal. It is split into 2 panels.
        Each panel has its own contents related to searching through the database
        or saving items into a watchlist/ favourites list.

        Left side contains:
        - A search for databases
        - Name of movie or actor
        - Search button
        - Results list
        - A recently viewed list
        - A quit application button

        The right side contains:
        - Favourites list
        - View favourites button
        - A watchlist
        - A view watchlist button

        The bottom contains:
        - Footer 
        """
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
        """
        This function runs when user searches either by pressing 'Enter'
        or pressing the search button. It reads the search input and
        clears old results. If the search is empty it raises an error. While
        searching it shows "Searching TMDB for ".

        Before pressing search:
        - User types something and presses enter
        - User types something and presses the search button

        After inputing the search:
        - Function reads the text
        - Old searches are cleared
        - Fetches data from the background
        - Puts search message while fetching data

        Raises an error:
        - if input is empty
        """
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
        """
        Searches for movies and actors in the background, combines the results,
        sorts in descending order of popularity and raises an exception if something
        goes wrong and sends it to the UI as a display error.

        Parameters:
        - self: 
        - query (str): movie or actor name

        Results:
        - movies and actors combined in descending order of popularity

        Raises an error:
        - if something goes wrong
        """
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
        """
        Shows the results of the search in a list format. If no results are found,
        show message on screen. For each search result, get the TMDB id of the movie/
        actor, title of the movie and release date. For actors, name of the actor and
        known for department. If unknown, write 'Unknown' on the screen. Show the results
        as a list. 

        After searching:
        - looks for widget in UI with id #results_list
        - makes sure it's a ListView
        - results stored in results_list
        - clear old searches

        For each movie search:
        - get the TMDB id
        - get the title (Unknown if not known)
        - get the release date

        For each actor search:
        - get the TMDB id
        - get the name of the actor (Unknown if not known)
        - get the department they are known for
        """
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
        """
        Function checks if search has a valid id. If not, exit. Checks
        if id starts with 'movie_' for movies or 'actor_' for actors. If it's
        a movie, show movie details. If it's an actor, show actor screen.

        Decorator:
        - listens for a selected event from the results list

        Parameters:
        - self
        - event: selected item from search results list

        Returns:
        - movie screen if id starts with 'movie_'
        - actor screen if id starts with 'actor_'
        - nothing if id doesn't exist
        - nothing if if id isn't in current_results
        """
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
        """
        Shows an error in the results list if something goes wrong.
        For example API error.

        Parameters:
        - self
        - error_msg(str): error message of what goes wrong

        Results:
        - Find ListView with id #results_list
        - clears all items in list
        - add message showing API error
        """
        results_list = self.query_one("#results_list", ListView)
        results_list.clear()
        results_list.append(ListItem(Label(f"API Error: {error_msg}")))

    def on_mount(self) -> None:
        """
        Lifecycle method in Textual that runs after first creating the screen
        and adds it to the UI. 

        Calls:
        - init_storage: local storage/ database
        - refresh_side_panels: refreshes the panels with up-to-date information
        """
        init_storage()
        self.refresh_side_panels()
    
    def on_screen_resume(self) -> None:
        """
        Called when the screen resumes and becomes active again. Refreshes
        the side panels with up-to-date information
        """
        self.refresh_side_panels()
    
    def refresh_side_panels(self) -> None:
        """
        Loads stored data using load_data. Finds ListView with specific
        id and updates specific list with stored data. If title/ actor
        is not known, show 'Unknown'. 

        Updated lists:
        - '#recent_list': recently viewed movies
        - '#favourites_list': favourite movies list
        - '#watch_preview_list' watchlist movies
        """
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
        """
        When the '#watchlist_button' is pressed, load data from stored data
        and display it on the screen under 'watchlist'
        """
        data = load_data()
        watchlist = data.get("watchlist", [])
        self.app.push_screen(CollectionScreen(ASCII_WATCHLIST, watchlist, "watchlist"))

    @on(Button.Pressed, "#favourites_button")
    def view_favourites(self) -> None:
        """
        When '#favourites_button' is pressed, load data from stored data
        and display it on the screen under 'favourites'
        """
        data = load_data()
        favourites = data.get("favourites", [])
        self.app.push_screen(CollectionScreen(ASCII_FAVOURITES, favourites, "favourites"))

    @on(Button.Pressed, "#quit_button")
    def action_quit_app(self) -> None:
        """
        When '#quit_button' is pressed, exit the application
        """
        self.app.exit()


class MovieScreen(Screen):
    def __init__(self, movie_data: dict):
        """
        Get movie data, which is stored as a dictionary, and add it to
        recently viewed list. Make an empty list for similar movies 

        Parameters:
        - self
        - movie_data(dict): movie data in the form of a dictionary
        """
        super().__init__()
        self.movie_data = movie_data
        add_to_recently_viewed(self.movie_data)
        self.similar_movies = []

    def compose(self) -> ComposeResult:
        """
        Show the results of movie searches and similar movies in list format.
        Footer at the bottom

        Contains:
        - title of the movie
        - release date
        - rating
        - overview. If none, add 'No overview available'
        - 'Add to favourites' button
        - 'Add to Watchlist' button
        - 'Back' button
        """
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
        """
        Get similar movies based on information of the selected movie
        """
        self.fetch_similar_movies_background()

    @work(thread=True)
    def fetch_similar_movies_background(self) -> None:
        """
        Find similar movies based on movie id in the background. If something goes
        wrong, call display_similar_error
        """
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
        """
        Find similar movies based on a list of movies. If no movies are
        similar, display 'No similar movies found'. If found, give details of
        the movies.

        Parameters:
        - movies(list): list of movies that are used to find similar movies

        Append similar movies to a list based on its id. Show movie title and
        release date. If movie title is uknown, then show 'Unknown'.
        """
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
        """
        Error if can't load similar movies.

        Parameters:
        - self
        - error_msg(str): error message in string format
        """
        list_view = self.query_one("#similar_list", ListView)
        list_view.clear()
        list_view.append(ListItem(Label(f"Error loading similar movies: {error_msg}")))

    @on(ListView.Selected, "#similar_list")
    def open_similar_movie(self, event: ListView.Selected) -> None:
        """
        Once user clicks on a movie in the '#similar_list', if the movie doesn't
        have an id, do nothing. Split the movie id to get only the numerical id, find
        the movie in similar_movies list and display the results on the screen
        """
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
        """
        When the '#back_button' is pressed, go to previous screen
        """
        self.app.pop_screen()

    @on(Button.Pressed, "#fav_button")
    def save_favourite(self) -> None:
        """
        When '#fav_button' is pressed, add movie to favourites and 
        display message
        """
        add_to_favourites(self.movie_data)
        self.notify("Added to Favourites!")

    @on(Button.Pressed, "#watch_list_button")
    def save_watchlist(self) -> None:
        """
        When '#watch_list_button' is pressed, add movie to
        watchlist and display message
        """
        add_to_watchlist(self.movie_data)
        self.notify("Added to Watchlist!")

class ActorScreen(Screen):
    def __init__(self, actor_data: dict):
        """
        Get actor data in the form of a dictionary and save the data
        internally. Prepare a dictionary for 'known for' movies
        """
        super().__init__()
        self.actor_data = actor_data
        self.known_for_map = {}

    def compose(self) -> ComposeResult:
        """
        Show the actor details that come up when searched for.

        Shows:
        - name: actor's name
        - department: genres they are known for
        - popularity: popularity score of the actor
        """
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
        """
        Get the actor's 'known for' movies and show it as a list. If there is
        no data, show an empty list. Clear old information. 
        
        Show:
        - title: title of movie. If unknown, then show 'Unknown'
        - release date: data when movie was released

        Save each item in 'known_for_map' for later handling. Set the
        selected index to be the first item
        """
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
        """
        When '#back_button' is pressed, go to previous screen
        """
        self.app.pop_screen()

    @on(ListView.Selected, "#known_for_list")
    def open_known_for(self, event: ListView.Selected) -> None:
        """
        When item is selected in '#known_for_list', look up the movie based on
        its id and show the details on the screen. If there is no id, do nothing
        """
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
        """
        Define title, movie list and collection type

        Parameters:
        - self
        - title (str): title of the movie
        - movie_list (list): display list of movies
        - collection_type(str): favourites or watchlist
        """
        super().__init__()
        self.display_title = title
        self.movies = movie_list
        self.collection_type = collection_type # e.g. favourites or watchlist
        self.movie_map = {} # Cache to map UI IDs to data

    def compose(self) -> ComposeResult:
        """
        Builds the UI for collection screen. There are vertical containers
        that contain header and buttons ('Back to Home' and 'Remove Selected') 
        and a ListView for collected items
        """
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
        """
        Displays '#collection_list' in ListView. If list is empty,
        display message. If not, show title of the movie and release
        date. The movie data is stored internally and is added to
        a visible movie list. Focus is set on the list so the user
        can immediately navigate
        """
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
        """
        When a movie from '#collection_list' is selected, the id of the movie
        is retrieved and it opens the details of the movie on the screen
        """
        movie = self.movie_map.get(event.item.id)
        if movie:
            self.app.push_screen(MovieScreen(movie))

    @on(Button.Pressed, "#back_to_home")
    def close_screen(self) -> None:
        """
        When '#back_to_home' button is pressed, it takes the user back to
        the home page
        """
        self.app.pop_screen()

    @on(Button.Pressed, "#remove_selected")
    def remove_item(self) -> None:
        """
        When '#remove_selected' button is pressed it deletes the selected item.
        If no item is selected, raises an error. It looks up the data
        of the movie and removes it from the UI. It notifies the user
        once an item has been deleted.
        """
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