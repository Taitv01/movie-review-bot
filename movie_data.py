"""
Movie Review Bot - Movie Data Fetcher
Fetches movie information from OMDB API (commercial use allowed).
Uses TMDB for images and trending (non-commercial fallback).
"""

import requests
from dataclasses import dataclass, field
from typing import Optional
from config import TMDB_API_KEY, OMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE, POSTER_SIZE, BACKDROP_SIZE


@dataclass
class MovieData:
    """Movie information container."""
    tmdb_id: int = 0
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


def fetch_movie_by_imdb(imdb_id: str) -> Optional[MovieData]:
    """Fetch movie details from OMDB using IMDB ID."""
    if not OMDB_API_KEY:
        print("Error: OMDB_API_KEY not set")
        return None

    url = "http://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "i": imdb_id,
        "plot": "full",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "False":
            print(f"Error: {data.get('Error', 'Movie not found')}")
            return None

        return _parse_omdb_data(data)

    except Exception as e:
        print(f"Error fetching movie: {e}")
        return None


def fetch_movie_by_title(title: str, year: int = 0) -> Optional[MovieData]:
    """Fetch movie details from OMDB using title."""
    if not OMDB_API_KEY:
        print("Error: OMDB_API_KEY not set")
        return None

    url = "http://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "plot": "full",
    }
    if year:
        params["y"] = year

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "False":
            print(f"Error: {data.get('Error', 'Movie not found')}")
            return None

        return _parse_omdb_data(data)

    except Exception as e:
        print(f"Error fetching movie: {e}")
        return None


def search_movies_omdb(query: str, page: int = 1) -> list[dict]:
    """Search for movies on OMDB."""
    if not OMDB_API_KEY:
        print("Error: OMDB_API_KEY not set")
        return []

    url = "http://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "s": query,
        "type": "movie",
        "page": page,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            return data.get("Search", [])
        return []

    except Exception as e:
        print(f"Error searching: {e}")
        return []


def _parse_omdb_data(data: dict) -> MovieData:
    """Parse OMDB API response into MovieData."""
    # Parse genres
    genre_str = data.get("Genre", "")
    genre_names = [g.strip() for g in genre_str.split(",") if g.strip()]
    genres = [{"name": g} for g in genre_names]

    # Parse cast
    cast_str = data.get("Actors", "")
    cast_names = [c.strip() for c in cast_str.split(",") if c.strip()]
    cast = [{"name": c} for c in cast_names]

    # Parse year
    year_str = data.get("Year", "0")
    year = int(year_str[:4]) if year_str and year_str[:4].isdigit() else 0

    # Parse runtime
    runtime_str = data.get("Runtime", "0 min")
    runtime = int(runtime_str.replace(" min", "")) if "min" in runtime_str else 0

    # Parse ratings
    imdb_rating = 0.0
    imdb_str = data.get("imdbRating", "N/A")
    if imdb_str != "N/A":
        try:
            imdb_rating = float(imdb_str)
        except:
            pass

    rotten_tomatoes = ""
    ratings = data.get("Ratings", [])
    for rating in ratings:
        if rating.get("Source") == "Rotten Tomatoes":
            rotten_tomatoes = rating.get("Value", "")
            break

    # Check if series
    is_series = data.get("Type") == "series"
    seasons = 0
    if is_series:
        total_seasons = data.get("totalSeasons", "0")
        seasons = int(total_seasons) if total_seasons.isdigit() else 0

    # Poster URL (OMDB provides poster, but may be "N/A")
    poster_url = data.get("Poster", "")
    if poster_url == "N/A":
        poster_url = ""

    movie = MovieData(
        tmdb_id=0,  # Will be set if TMDB is used
        imdb_id=data.get("imdbID", ""),
        title=data.get("Title", ""),
        original_title=data.get("Title", ""),
        year=year,
        overview=data.get("Plot", ""),
        rating=imdb_rating,  # Use IMDB rating as main rating
        imdb_rating=imdb_rating,
        rotten_tomatoes=rotten_tomatoes,
        genres=genres,
        genre_names=genre_names,
        director=data.get("Director", ""),
        cast=cast,
        cast_names=cast_names,
        poster_url=poster_url,
        backdrop_url="",  # OMDB doesn't provide backdrop
        tagline="",
        runtime=runtime,
        budget=0,
        revenue=0,
        status=data.get("Status", ""),
        language=data.get("Language", ""),
        production_companies=[],
        is_series=is_series,
        seasons=seasons,
        episodes=0,
    )

    return movie


def fetch_movie_details(tmdb_id: int, media_type: str = "movie") -> Optional[MovieData]:
    """Fetch movie details - tries TMDB first, falls back to OMDB."""
    # Try TMDB first (for images and detailed data)
    if TMDB_API_KEY:
        movie = _fetch_from_tmdb(tmdb_id, media_type)
        if movie:
            return movie

    # Fallback: Cannot fetch by TMDB ID without TMDB API
    print("Error: TMDB API required for fetching by TMDB ID")
    return None


def _fetch_from_tmdb(tmdb_id: int, media_type: str = "movie") -> Optional[MovieData]:
    """Fetch from TMDB API."""
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

        return movie

    except Exception as e:
        print(f"Error fetching from TMDB: {e}")
        return None


def fetch_trending_movies(media_type: str = "movie", time_window: str = "week", page: int = 1) -> list[dict]:
    """Fetch trending movies/series from TMDB."""
    if not TMDB_API_KEY:
        print("Warning: TMDB_API_KEY not set, cannot fetch trending")
        return []

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


def search_movies(query: str, page: int = 1) -> list[dict]:
    """Search for movies - uses OMDB if available, TMDB otherwise."""
    if OMDB_API_KEY:
        return search_movies_omdb(query, page)

    # Fallback to TMDB
    if TMDB_API_KEY:
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
    if not TMDB_API_KEY:
        return []

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
    if not TMDB_API_KEY:
        return []

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
    print("Testing OMDB API...")
    print(f"OMDB API Key set: {'Yes' if OMDB_API_KEY else 'No'}")
    print(f"TMDB API Key set: {'Yes' if TMDB_API_KEY else 'No'}")

    if OMDB_API_KEY:
        # Test search
        print("\nSearching for 'Fight Club'...")
        results = search_movies_omdb("Fight Club")
        if results:
            print(f"Found {len(results)} results")
            first = results[0]
            print(f"First result: {first.get('Title')} ({first.get('Year')})")

            # Fetch details
            imdb_id = first.get("imdbID")
            if imdb_id:
                print(f"\nFetching details for IMDB ID: {imdb_id}...")
                movie = fetch_movie_by_imdb(imdb_id)
                if movie:
                    print(f"Title: {movie.title} ({movie.year})")
                    print(f"Rating: {movie.rating}/10")
                    print(f"IMDB: {movie.imdb_rating}/10")
                    print(f"Rotten Tomatoes: {movie.rotten_tomatoes}")
                    print(f"Director: {movie.director}")
                    print(f"Cast: {', '.join(movie.cast_names)}")
                    print(f"Genres: {', '.join(movie.genre_names)}")
                    print(f"Poster: {movie.poster_url}")
                    print(f"Plot: {movie.overview[:200]}...")
        else:
            print("No results found")
    else:
        print("\nTo use OMDB API:")
        print("1. Go to http://www.omdbapi.com/apikey.aspx")
        print("2. Register for free API key")
        print("3. Add to .env: OMDB_API_KEY=your_key")
        print("\nFree tier: 1,000 requests/day, commercial use allowed")
