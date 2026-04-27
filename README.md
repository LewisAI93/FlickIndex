# 🎬 FlickIndex

FlickIndex is a simple movie discovery application that allows you to search for movie recommendations to watch. The app has a user friendly database that is powered by the TMDB API. This helps you find what to watch faster, instead of what feels like endless scrolling through cluttered streaming menus with results you have no interest in.

## ✨ Features
- 🔍 Search for movies by title, actor, or genre
- 🗂️ Browse movies by genre with instant results
- ⚡ Fast access to movie details and similar titles
- 👀 User-friendly terminal interface built with Textual
- ⭐ Favourites list
- 🍿 Watchlist
- 🕒 Recently viewed list
- 🔥 Popular movies list

## 📁 Project Structure
- `main.py` — Textual app
- `tmdb_client.py` — TMDB API functions
- `storage_module.py` — Local data persistence
- `flickindex.tcss` — App styling

## Setup & Run

1. Request an API key from TMDB - https://developer.themoviedb.org/docs/getting-started
    

2. Create a `.env` file in the project folder and add your key:
    
    ```env
    TMDB_API_KEY="your_api_key_here"
    ```

3. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Start the application:

    ```bash
    python3 main.py
    ```

## Basic Controls

- **Mouse compatible** — most actions can be performed with clicks.
- **Navigate** — use the mouse, or press `Tab` / `Shift+Tab` to move focus and `Enter` to select.
- **Go Back** — press `Escape` at any time to return to the previous screen.
- **Standard Search** — type a movie or actor name and press `Enter`.
- **Genre Search** — type `genre:` followed by a genre name (e.g. `genre: sci-fi`).
- **Browse Genres** — use the Browse Genres button to visually explore movies by category.
- **Open from Collections** — double-click a title in your Favourites or Watchlist to view its details.
- **Delete from Collections** — single-click to select an item, then press `d` or click Remove Selected.
