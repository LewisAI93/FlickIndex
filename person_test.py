#### TESTING FOR ACTOR & DIRECTOR SEARCH ####

from main import search_actor

def main():
    query = input("Actor name: ")
    people = search_actor(query)
    print(f"Found {len(people)} people")
    for p in people[:5]:
        name = p.get("name")
        dept = p.get("known_for_department")
        known_for = p.get("known_for") or []
        titles = [item.get("title") or item.get("name") for item in known_for]
        print(f"- {name} ({dept})")
        if titles:
            print("  Known for: " + ", ".join(t for t in titles if t))

if __name__ == "__main__":
    main()