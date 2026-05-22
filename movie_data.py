"""
Movie Review Bot - Movie Data Fetcher
Fetches movie information from TMDB and OMDB APIs.
"""

import requests
from dataclasses import dataclass, field
from typing import Optional
from config import TMDB_API_KEY, OMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE, POSTER_SIZE, BACKDROP_SIZE


@dataclass
class MovieData:
    """Movie information container."""
    tmdb_id: int
    imdb_id: str = ""
    title: str = ""
    original_title: str = ""
    year: int = 0
    overview: str = ""
    rating: float = 0.0
    imdb_rating: float = 0.0
    rotten_tomatoes: str = ""
    genres: list = field(default_factory=list)
    genre_names: list = field(default_factory=list)
    director: str = ""
    cast: list = field(default_factory=list)
    cast_names: list = field(default_factory=list)
    poster_url: str = ""
    backdrop_url: str = ""
    tagline: str = ""
    runtime: int = 0
    budget: int = 0
    revenue: int = 0
    status: str = ""
    language: str = ""
    production_companies: list = field(default_factory=list)
    is_series: bool = False
    seasons: int = 0
    episodes: int = 0


def fetch_trending_movies(media_type: str = "movie", time_window: str = "week", page: int = 1) -> list[dict]:
    """Fetch trending movies/series from TMDB."""
    url = f"{TMDB_BASE_URL}/trending/{media_type}/{time_window}"
    params = {
        "api_key": TMDB_API_KEY,
        "page": page,
        "language": "en-US",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error fetching trending: {e}")
        return []


def fetch_movie_details(tmdb_id: int, media_type: str = "movie") -> Optional[MovieData]:
    """Fetch detailed movie information from TMDB."""
    url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "append_to_response": "credits,videos",
        "language": "en-US",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract basic info
        title = data.get("title") or data.get("name", "")
        original_title = data.get("original_title") or data.get("original_name", "")
        release_date = data.get("release_date") or data.get("first_air_date", "")
        year = int(release_date[:4]) if release_date else 0

        # Extract genres
        genres = data.get("genres", [])
        genre_names = [g["name"] for g in genres]

        # Extract credits
        credits = data.get("credits", {})
        crew = credits.get("crew", [])
        cast = credits.get("cast", [])

        # Find director
        director = ""
        for person in crew:
            if person.get("job") == "Director":
                director = person.get("name", "")
                break

        # For TV series, find creator
        if media_type == "tv":
            creators = data.get("created_by", [])
            if creators:
                director = creators[0].get("name", director)

        # Extract cast (top 5)
        cast_list = cast[:5]
        cast_names = [c.get("name", "") for c in cast_list]

        # Build image URLs
        poster_path = data.get("poster_path", "")
        backdrop_path = data.get("backdrop_path", "")
        poster_url = f"{TMDB_IMAGE_BASE}/{POSTER_SIZE}{poster_path}" if poster_path else ""
        backdrop_url = f"{TMDB_IMAGE_BASE}/{BACKDROP_SIZE}{backdrop_path}" if backdrop_path else ""

        # Series-specific info
        is_series = media_type == "tv"
        seasons = data.get("number_of_seasons", 0)
        episodes = data.get("number_of_episodes", 0)

        movie = MovieData(
            tmdb_id=tmdb_id,
            imdb_id=data.get("imdb_id", ""),
            title=title,
            original_title=original_title,
            year=year,
            overview=data.get("overview", ""),
            rating=round(data.get("vote_average", 0), 1),
            genres=genres,
            genre_names=genre_names,
            director=director,
            cast=cast_list,
            cast_names=cast_names,
            poster_url=poster_url,
            backdrop_url=backdrop_url,
            tagline=data.get("tagline", ""),
            runtime=data.get("runtime", 0) or data.get("episode_run_time", [0])[0] if data.get("episode_run_time") else 0,
            budget=data.get("budget", 0),
            revenue=data.get("revenue", 0),
            status=data.get("status", ""),
            language=data.get("original_language", ""),
            production_companies=data.get("production_companies", []),
            is_series=is_series,
            seasons=seasons,
            episodes=episodes,
        )

        # Fetch IMDB/Rotten Tomatoes ratings from OMDB
        if movie.imdb_id:
            _fetch_omdb_ratings(movie)

        return movie

    except Exception as e:
        print(f"Error fetching movie details: {e}")
        return None


def _fetch_omdb_ratings(movie: MovieData) -> None:
    """Fetch IMDB and Rotten Tomatoes ratings from OMDB."""
    if not OMDB_API_KEY:
        return

    url = "http://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "i": movie.imdb_id,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            # IMDB rating
            imdb_rating = data.get("imdbRating", "N/A")
            if imdb_rating != "N/A":
                movie.imdb_rating = float(imdb_rating)

            # Rotten Tomatoes
            ratings = data.get("Ratings", [])
            for rating in ratings:
                if rating.get("Source") == "Rotten Tomatoes":
                    movie.rotten_tomatoes = rating.get("Value", "")
                    break

    except Exception as e:
        print(f"Error fetching OMDB data: {e}")


def search_movies(query: str, page: int = 1) -> list[dict]:
    """Search for movies on TMDB."""
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "page": page,
        "language": "en-US",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error searching: {e}")
        return []


def download_image(url: str, save_path: str) -> bool:
    """Download an image from URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False


def get_popular_movies(language: str = "en-US", page: int = 1) -> list[dict]:
    """Get popular movies from TMDB."""
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "page": page,
        "language": language,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error fetching popular: {e}")
        return []


def get_top_rated_movies(language: str = "en-US", page: int = 1) -> list[dict]:
    """Get top rated movies from TMDB."""
    url = f"{TMDB_BASE_URL}/movie/top_rated"
    params = {
        "api_key": TMDB_API_KEY,
        "page": page,
        "language": language,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error fetching top rated: {e}")
        return []


# ── Test Function ────────────────────────────────────────────
if __name__ == "__main__":
    # Test fetching trending movies
    print("Fetching trending movies...")
    trending = fetch_trending_movies()
    if trending:
        print(f"Found {len(trending)} trending movies")
        first = trending[0]
        print(f"First movie: {first.get('title', 'N/A')} ({first.get('release_date', 'N/A')})")

        # Fetch details for first movie
        tmdb_id = first.get("id")
        if tmdb_id:
            print(f"\nFetching details for TMDB ID: {tmdb_id}...")
            movie = fetch_movie_details(tmdb_id)
            if movie:
                print(f"Title: {movie.title} ({movie.year})")
                print(f"Rating: {movie.rating}/10")
                print(f"IMDB: {movie.imdb_rating}/10")
                print(f"Rotten Tomatoes: {movie.rotten_tomatoes}")
                print(f"Director: {movie.director}")
                print(f"Cast: {', '.join(movie.cast_names)}")
                print(f"Genres: {', '.join(movie.genre_names)}")
                print(f"Poster: {movie.poster_url}")
    else:
        print("No trending movies found. Check your TMDB API key.")
