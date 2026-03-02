from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static

from main import search_movies

class FlickIndex(App):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Type a movie name and press Enter...", id="search_input")
        yield Static("Results will appear here.", id="results")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#search_input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        results_box = self.query_one("#results", Static)

        if not query:
            results_box.update("Please type a movie title.")
            return

        try:
            movies = search_movies(query)
        except Exception as e:
            results_box.update(f"Error talking to TMDB: {e}")
            return

        if not movies:
            results_box.update("No movies found.")
            return

        lines = []
        for movie in movies[:5]:
            title = movie.get("title") or "Unknown title"
            year = (movie.get("release_date") or "")[:4]
            rating = movie.get("vote_average")
            if year:
                title_line = f"{title} ({year})"
            else:
                title_line = title
            if rating is not None:
                title_line += f"  ⭐ {rating}"
            lines.append(title_line)

        results_box.update("\n".join(lines))

if __name__ == "__main__":
    FlickIndex().run()
