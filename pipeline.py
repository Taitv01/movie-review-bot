"""
Movie Review Bot - Main Pipeline
Orchestrates all steps to create and upload movie review videos.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from movie_data import fetch_trending_movies, fetch_movie_details, download_image, MovieData
from script_generator import generate_review_script, generate_title, generate_description, generate_tags
from voice_generator import generate_movie_audio
from subtitle_generator import generate_subtitles
from thumbnail_generator import generate_thumbnail
from video_builder import build_video
from youtube_uploader import upload_video
from config import (
    CHANNEL_LANGUAGE,
    CHANNEL_NAME,
    THUMBNAILS_DIR,
    VIDEOS_DIR,
    AUDIO_DIR,
    SUBTITLES_DIR,
)


def process_movie(
    tmdb_id: int,
    media_type: str = "movie",
    language: str = None,
    upload: bool = False,
    privacy: str = "private",
) -> Optional[str]:
    """Process a single movie: fetch data, generate script, build video, upload."""
    language = language or CHANNEL_LANGUAGE
    start_time = time.time()

    print(f"\n{'='*60}")
    print(f"Processing Movie ID: {tmdb_id}")
    print(f"Language: {language}")
    print(f"{'='*60}\n")

    # Step 1: Fetch movie data
    print("[1/7] Fetching movie data...")
    movie = fetch_movie_details(tmdb_id, media_type)
    if not movie:
        print("Error: Failed to fetch movie data")
        return None

    print(f"  Title: {movie.title} ({movie.year})")
    print(f"  Rating: {movie.rating}/10")
    print(f"  Genres: {', '.join(movie.genre_names)}")

    # Step 2: Generate review script
    print("\n[2/7] Generating review script...")
    script = generate_review_script(movie, language)
    if not script:
        print("Error: Failed to generate script")
        return None

    word_count = len(script.split())
    print(f"  Script generated: {word_count} words")

    # Step 3: Generate audio
    print("\n[3/7] Generating audio...")
    audio_path = generate_movie_audio(script, movie.tmdb_id, language)
    if not audio_path:
        print("Error: Failed to generate audio")
        return None

    # Step 4: Generate subtitles
    print("\n[4/7] Generating subtitles...")
    subtitle_path = generate_subtitles(script, movie.tmdb_id, language)
    if not subtitle_path:
        print("Error: Failed to generate subtitles")
        return None

    # Step 5: Generate thumbnail
    print("\n[5/7] Generating thumbnail...")
    thumbnail_path = generate_thumbnail(movie, language=language)
    if not thumbnail_path:
        print("Warning: Failed to thumbnail, continuing without it")

    # Step 6: Download background images
    print("\n[6/7] Downloading background images...")
    background_images = download_background_images(movie)

    # Step 7: Build video
    print("\n[7/7] Building video...")
    video_path = build_video(
        movie=movie,
        audio_path=audio_path,
        subtitle_path=subtitle_path,
        thumbnail_path=thumbnail_path,
        language=language,
        background_images=background_images,
    )
    if not video_path:
        print("Error: Failed to build video")
        return None

    # Upload to YouTube
    if upload:
        print("\n[UPLOAD] Uploading to YouTube...")
        title = generate_title(movie, language)
        description = generate_description(movie, script, language)
        tags = generate_tags(movie, language)

        video_id = upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            thumbnail_path=thumbnail_path,
            privacy=privacy,
            language=language,
        )

        if video_id:
            print(f"\n✅ Video uploaded: https://www.youtube.com/watch?v={video_id}")
        else:
            print("\n❌ Failed to upload video")

    # Summary
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"Time elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"Video saved to: {video_path}")
    print(f"{'='*60}\n")

    return video_path


def download_background_images(movie: MovieData) -> list[str]:
    """Download background images for video."""
    images = []

    # Download poster
    if movie.poster_url:
        poster_path = str(THUMBNAILS_DIR / f"{movie.tmdb_id}_poster.jpg")
        if download_image(movie.poster_url, poster_path):
            images.append(poster_path)

    # Download backdrop
    if movie.backdrop_url:
        backdrop_path = str(THUMBNAILS_DIR / f"{movie.tmdb_id}_backdrop.jpg")
        if download_image(movie.backdrop_url, backdrop_path):
            images.append(backdrop_path)

    print(f"  Downloaded {len(images)} background images")
    return images


def process_trending(
    count: int = 1,
    media_type: str = "movie",
    language: str = None,
    upload: bool = False,
    privacy: str = "private",
) -> list[str]:
    """Process trending movies."""
    language = language or CHANNEL_LANGUAGE

    print(f"\nFetching trending {media_type}s...")
    trending = fetch_trending_movies(media_type)

    if not trending:
        print("No trending movies found")
        return []

    print(f"Found {len(trending)} trending {media_type}s")

    # Process first N movies
    results = []
    for i, item in enumerate(trending[:count]):
        tmdb_id = item.get("id")
        if tmdb_id:
            print(f"\nProcessing {i+1}/{count}...")
            video_path = process_movie(
                tmdb_id=tmdb_id,
                media_type=media_type,
                language=language,
                upload=upload,
                privacy=privacy,
            )
            if video_path:
                results.append(video_path)

    return results


def process_custom_list(
    movie_ids: list[int],
    media_type: str = "movie",
    language: str = None,
    upload: bool = False,
    privacy: str = "private",
) -> list[str]:
    """Process a custom list of movies."""
    language = language or CHANNEL_LANGUAGE

    results = []
    for i, tmdb_id in enumerate(movie_ids):
        print(f"\nProcessing {i+1}/{len(movie_ids)}...")
        video_path = process_movie(
            tmdb_id=tmdb_id,
            media_type=media_type,
            language=language,
            upload=upload,
            privacy=privacy,
        )
        if video_path:
            results.append(video_path)

    return results


# ── Command Line Interface ───────────────────────────────────
def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Movie Review Bot")
    parser.add_argument(
        "--movie-id",
        type=int,
        help="TMDB movie ID to process",
    )
    parser.add_argument(
        "--trending",
        action="store_true",
        help="Process trending movies",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of movies to process (default: 1)",
    )
    parser.add_argument(
        "--type",
        choices=["movie", "tv"],
        default="movie",
        help="Media type (default: movie)",
    )
    parser.add_argument(
        "--language",
        choices=["vi", "en"],
        default=None,
        help="Language (default: from config)",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload to YouTube",
    )
    parser.add_argument(
        "--privacy",
        choices=["public", "private", "unlisted"],
        default="private",
        help="YouTube privacy status (default: private)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.movie_id and not args.trending:
        parser.error("Either --movie-id or --trending must be specified")

    # Process
    if args.trending:
        results = process_trending(
            count=args.count,
            media_type=args.type,
            language=args.language,
            upload=args.upload,
            privacy=args.privacy,
        )
    else:
        video_path = process_movie(
            tmdb_id=args.movie_id,
            media_type=args.type,
            language=args.language,
            upload=args.upload,
            privacy=args.privacy,
        )
        results = [video_path] if video_path else []

    # Summary
    print(f"\n{'='*60}")
    print(f"Processed {len(results)} videos successfully")
    for path in results:
        print(f"  - {path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
