from tmdb_client import search_by_title, search_by_actor

while True:
    print("-------------------")
    print("1. Search by movie")
    print("2. Search by actor")
    print("3. Quit")
    print("-------------------")
    user_input = input("Choose a numbered option: ")

    if user_input == "1":
        movie_name = input("\nEnter a movie name:")
        results = search_by_title(movie_name)

        if not results:
            print("No results found.")
        else:
            for movie in results[:5]:
                title = movie.get("title", "Unknown title")
                release_date = movie.get("release_date", "")
                year = release_date[:4] if release_date else "----"
                rating = movie.get("vote_average", "N/A")
                print(f"\n{title} ({year}) - Rating: {rating}")

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
                for work in known_for_list:
                    title = work.get("title") or work.get("name", "Unknown title")
                    print(f"  - {title}")
            print()

    elif user_input.lower() == "3":
        break

    else:
        print("Please choose option '1', '2' or '3'\n")
        continue