from dataclasses import dataclass, asdict


@dataclass
class Movie:
    movie_id: str
    title: str
    plot: str
    release_year: int
    genre: str
    rating: float
    votes: int
    imdb_id: str

    @property
    def redis_key(self) -> str:
        return f"movie:{self.movie_id}"

    def to_redis_hash(self) -> dict:
        data = asdict(self)
        data.pop("movie_id")
        return data

    @classmethod
    def from_redis_hash(cls, key: str, data: dict) -> "Movie":
        movie_id = key.split(":")[-1]
        return cls(
            movie_id=movie_id,
            title=data.get("title", ""),
            plot=data.get("plot", ""),
            release_year=int(data.get("release_year", 0)),
            genre=data.get("genre", ""),
            rating=float(data.get("rating", 0.0)),
            votes=int(data.get("votes", 0)),
            imdb_id=data.get("imdb_id", ""),
        )
