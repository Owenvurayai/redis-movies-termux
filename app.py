from models import Movie
from repository import MovieRepository

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "password": None,
}


def seed_sample_movies(repo: MovieRepository):
    samples = [
        Movie(
            movie_id="11003",
            title="The Godfather",
            plot="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            release_year=1972,
            genre="Drama",
            rating=9.2,
            votes=1563839,
            imdb_id="tt0068646",
        ),
        Movie(
            movie_id="11004",
            title="Heat",
            plot="A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist.",
            release_year=1995,
            genre="Thriller",
            rating=8.2,
            votes=559490,
            imdb_id="tt0113277",
        ),
        Movie(
            movie_id="11005",
            title="Star Wars: Episode VI - Return of the Jedi",
            plot="The Rebels dispatch to Endor to destroy the second Empire's Death Star.",
            release_year=1983,
            genre="Action",
            rating=8.3,
            votes=906260,
            imdb_id="tt0086190",
        ),
    ]
    for m in samples:
        repo.save_movie(m)
    print(f"Loaded {len(samples)} sample movies into Redis.")


def display_movies(movies: list[Movie]):
    if not movies:
        print("\nNo matching movies found.")
        return
    print(f"\n--- Found {len(movies)} Movie(s) ---")
    for m in movies:
        print(f"[{m.movie_id}] {m.title} ({m.release_year}) | Genre: {m.genre} | Rating: {m.rating}")
        print(f"   Plot: {m.plot}\n")


def main():
    repo = MovieRepository(**REDIS_CONFIG)
    print(repo.create_index())
    seed_sample_movies(repo)

    while True:
        print("\n=== RediSearch Movie App ===")
        print("1. List all movies (sorted by highest rating)")
        print("2. Search by title/text (e.g., Heat, Jedi)")
        print("3. Filter by genre tag (e.g., Drama, Thriller, Action)")
        print("4. Filter by minimum rating (e.g., 8.5)")
        print("5. Add a new movie")
        print("6. View index stats")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            display_movies(repo.search_movies("*", sort_by="rating", ascending=False))
        elif choice == "2":
            term = input("Enter search text: ").strip()
            display_movies(repo.search_movies(term))
        elif choice == "3":
            genre = input("Enter genre (Drama/Thriller/Action): ").strip()
            display_movies(repo.search_movies(f"@genre:{{{genre}}}"))
        elif choice == "4":
            min_r = input("Minimum rating (e.g. 8.5): ").strip()
            display_movies(repo.search_movies(f"@rating:[{min_r} 10]", sort_by="rating", ascending=False))
        elif choice == "5":
            m = Movie(
                movie_id=input("Movie ID (e.g. 11006): ").strip(),
                title=input("Title: ").strip(),
                plot=input("Plot: ").strip(),
                release_year=int(input("Release Year: ").strip()),
                genre=input("Genre: ").strip(),
                rating=float(input("Rating (0-10): ").strip()),
                votes=int(input("Votes: ").strip()),
                imdb_id=input("IMDb ID: ").strip(),
            )
            repo.save_movie(m)
            print("Saved! Secondary indexes updated automatically.")
        elif choice == "6":
            print("Index Stats:", repo.get_index_stats())
        elif choice == "0":
            break


if __name__ == "__main__":
    main()
