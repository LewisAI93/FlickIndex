#### TESTING FOR MOVIE SEARCH ####

from main import search_movies

def main():
    query = input("Movie title: ")
    movies = search_movies(query)
    print(f"Found {len(movies)} movies")
    for m in movies[:5]:
        title = m.get("title")
        year = (m.get("release_date") or "")[:4]
        rating = m.get("vote_average")
        print(f"- {title} ({year}) rating: {rating}")

if __name__ == "__main__":
    main()
