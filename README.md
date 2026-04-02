# 🎬 FlickIndex

FlickIndex is a simple movie discovery application that allows you to search for movie recommendations to watch. The app has a user friendly database that is powered by the TMDB API. This helps you find what to watch faster, instead of what feels like endless scrolling through cluttered streaming menus with results you have no interest in.

## ✨ Upcoming Features
- 🔍 Search for movies by title, actor and director.
- 🗂️ Clean and driven by the TMDB API
- ⚡ Fast access to movie details
- 👀 User friendly Textual interface.

## ❓ Possible Future Features

- ⭐ Favourites list
- 🍿 Watch list
- 🕒 Recently viewed list


## Setup & Run

- Request an API key from TMDB - https://developer.themoviedb.org/docs/getting-started

- Create a `.env` file in the project folder and add your key: `TMDB_API_KEY=your_api_key_here`

- Create and activate a venv: `python -m venv venv` > `source venv/bin/activate`

- Install dependencies: `pip install -r requirements.txt`

- Start the application:` python3 app.py`


## Basic Controls

- Mouse compatible.

- Navigate: Use the mouse, or press `Tab` / `Shift+Tab` to move focus and Enter to select.

- Go Back: Press `Escape` at any time to return to the previous screen.

- Standard Search: Type a movie or actor name and press Enter.

- Genre Search: Type `genre`:  followed by the genre name (e.g., genre: sci-fi).

- Manage Collections: In your Favourites or Watchlist, select an item and press d to delete it.