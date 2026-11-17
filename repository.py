import re
import redis
from models import Movie


class MovieRepository:
    KEY_PREFIX = "movie:"

    def __init__(self, host="localhost", port=6379, password=None):
        self.client = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
        )

    def create_index(self) -> str:
        return "OK - Using native Redis secondary indexes (Sets + Sorted Sets)."

    def _tokenize(self, text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", text.lower()))

    def save_movie(self, movie: Movie) -> None:
        pipe = self.client.pipeline()
        pipe.hset(movie.redis_key, mapping=movie.to_redis_hash())
        pipe.zadd("idx:rating", {movie.movie_id: movie.rating})
        pipe.sadd(f"idx:genre:{movie.genre.lower()}", movie.movie_id)
        words = self._tokenize(f"{movie.title} {movie.plot}")
        for word in words:
            pipe.sadd(f"idx:word:{word}", movie.movie_id)
        pipe.execute()

    def get_movie_by_id(self, movie_id: str) -> Movie | None:
        key = f"{self.KEY_PREFIX}{movie_id}"
        data = self.client.hgetall(key)
        return Movie.from_redis_hash(key, data) if data else None

    def _fetch_movies(self, movie_ids: list[str]) -> list[Movie]:
        movies = []
        for mid in movie_ids:
            movie = self.get_movie_by_id(mid)
            if movie:
                movies.append(movie)
        return movies

    def search_movies(self, query_str: str = "*", sort_by: str = None, ascending: bool = False) -> list[Movie]:
        query_str = query_str.strip()

        if query_str == "*":
            if ascending:
                ids = self.client.zrange("idx:rating", 0, -1)
            else:
                ids = self.client.zrevrange("idx:rating", 0, -1)
            return self._fetch_movies(ids)

        if query_str.startswith("@genre:{") and query_str.endswith("}"):
            genre = query_str[8:-1].lower()
            ids = list(self.client.smembers(f"idx:genre:{genre}"))
            return self._fetch_movies(ids)

        if query_str.startswith("@rating:[") and query_str.endswith("]"):
            bounds = query_str[9:-1].split()
            min_r, max_r = float(bounds[0]), float(bounds[1])
            ids = self.client.zrangebyscore("idx:rating", min_r, max_r)
            if not ascending:
                ids.reverse()
            return self._fetch_movies(ids)

        tokens = self._tokenize(query_str)
        if not tokens:
            return []
        word_keys = [f"idx:word:{t}" for t in tokens]
        matching_ids = list(self.client.sinter(word_keys))
        return self._fetch_movies(matching_ids)

    def get_index_stats(self) -> dict:
        return {
            "engine": "Redis Core (Manual Secondary Indexes)",
            "indexed_movies": self.client.zcard("idx:rating"),
            "word_index_keys": len(self.client.keys("idx:word:*")),
            "genre_index_keys": len(self.client.keys("idx:genre:*")),
        }
