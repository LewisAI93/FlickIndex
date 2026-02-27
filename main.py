from tmdb_client import search_by_title, search_by_actor, search_by_director, search_related_movies, search_by_genre

def movie_list(movie):
    title = movie.get("title", "Unknown title")
    release_date = movie.get("release_date", "")
    year = release_date[:4] if release_date else "----"
    rating = movie.get("vote_average", "N/A")
    synopsis = movie.get("overview", "No overview available.")
    popularity = movie.get("popularity", "N/A")

    print("\n--- Movie details ---")
    print(f"Title: {title} ({year}) - Rating: {rating} - Popularity: {popularity}")
    print(f"Synopsis: {synopsis}\n")

def related_movies(start_movie):
    current = start_movie

    while True:
        movie_list(current)
        movie_id = current.get("id")
        if movie_id is None:
            print("No ID for this movie, cannot find similar.\n")
            break

        related_movies = search_related_movies(movie_id)
        if not related_movies:
            print("No similar movies found.\n")
            break

        print("Similar movies:")
        for index, movie in enumerate(related_movies[:5], start=1):
            title = movie.get("title", "Unknown title")
            release_date = movie.get("release_date", "")
            year = release_date[:4] if release_date else "----"
            rating = movie.get("vote_average", "N/A")
            print(f"{index}. {title} ({year}) - Rating: {rating}")

        choice = input("\nPick a similar movie by number, or press Enter to go back: ")

        if choice == "":
            break
        if not choice.isdigit():
            print("That is not a valid number.\n")
            continue

        choice_index = int(choice) - 1
        if 0 <= choice_index < len(related_movies[:5]):
            current = related_movies[choice_index]
        else:
            print("Please enter a number from the list.\n")

while True:
    print("-------------------")
    print("1. Search by movie")
    print("2. Search by actor")
    print("3. Search by director")
    print("4. Search by genre")
    print("5. Quit")
    print("-------------------")
    user_input = input("Choose a numbered option: ")

    if user_input == "1":
        movie_name = input("\nEnter a movie name: ")
        results = search_by_title(movie_name)
        print()

        if not results:
            print("No results found.")
        else:
            top_movies = results[:5]
            for index, movie in enumerate(top_movies, start=1):
                title = movie.get("title", "Unknown title")
                release_date = movie.get("release_date", "")
                year = release_date[:4] if release_date else "----"
                rating = movie.get("vote_average", "N/A")
                print(f"{index}. {title} ({year}) - Rating: {rating}")
        while True:
            choice = input("\nEnter a number to select a movie (or press Enter to go back): ")

            if choice == "":
                break
            elif choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(top_movies):
                    selected = top_movies[choice_index]
                    related_movies(selected)
                    break
                else:
                    print("Please enter a number from the list.")
            else:
                print("That is not a valid number.")

    elif user_input == "2":
        actor_name = input("\nEnter an actor's name: ")
        results = search_by_actor(actor_name)

        if not results:
            print("No results found.")
        else:
            for person in results[:3]:
                name = person.get("name", "Unknown name")
                known_for_list = person.get("known_for", [])

                if known_for_list:
                    print(f"\n{name} is known for:")
                    for index, work in enumerate(known_for_list[:5], start=1):
                        title = work.get("title") or work.get("name", "Unknown title")
                        year = (work.get("release_date") or "")[:4]
                        rating = work.get("vote_average", "N/A")
                        print(f"{index}. {title} ({year}) - Rating: {rating}")
                else:
                    print(f"\nNo 'known for' titles found for {name}.")
            print()

    elif user_input == "3":
        director_name = input("\nEnter a director's name: ")
        directed = search_by_director(director_name)

        if not directed:
            print("No directing credits found.")
        else:
            print(f"\nMovies directed by {director_name}:")
            directed = sorted(
                directed,
                key=lambda m: m.get("release_date") or "",
                reverse=True
            )
            for index, movie in enumerate(directed[:10], start=1):
                title = movie.get("title", "Unknown title")
                year = (movie.get("release_date") or "")[:4]
                rating = movie.get("vote_average", "N/A")
                print(f" {index}. {title} ({year}) - Rating: {rating}")
        print()

####WIP### Lewis

    elif user_input == "4":
         genre_name = input("\nEnter a genre name: ")
         genre = search_by_genre(genre_name)

    elif user_input.lower() == "5":
        break

    else:
        print("Please choose option '1', '2' or '3'\n")
        continue