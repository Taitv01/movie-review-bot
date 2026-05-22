"""
Movie Review Bot - Script Generator
Uses DeepSeek API (free tier) to generate movie review scripts.

DeepSeek free tier: Much more generous than Gemini
- No strict daily limit
- High quality for long-form content
- OpenAI-compatible API
"""

import requests
import json
from typing import Optional
from movie_data import MovieData
from config import CHANNEL_LANGUAGE, MIN_WORD_COUNT, SCRIPT_PROMPTS

# DeepSeek API configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Import API key from config
try:
    from config import DEEPSEEK_API_KEY
except ImportError:
    DEEPSEEK_API_KEY = ""


def generate_review_script(movie: MovieData, language: str = None) -> Optional[str]:
    """Generate a movie review script using DeepSeek AI."""
    if not DEEPSEEK_API_KEY:
        print("Error: DEEPSEEK_API_KEY not set")
        print("Get free API key at: https://platform.deepseek.com")
        return None

    language = language or CHANNEL_LANGUAGE

    # Determine if movie or series
    content_type = "series" if movie.is_series else "movie"

    # Get the prompt template
    prompt_template = SCRIPT_PROMPTS[language][content_type]

    # Fill in movie details
    prompt = prompt_template.format(
        title=movie.title,
        year=movie.year,
        genres=", ".join(movie.genre_names),
        director=movie.director,
        cast=", ".join(movie.cast_names),
        rating=movie.rating,
        overview=movie.overview,
        season=movie.seasons if movie.is_series else "",
        episodes=movie.episodes if movie.is_series else "",
    )

    # Add word count requirement
    min_words = MIN_WORD_COUNT[language]
    prompt += f"\n\nIMPORTANT: The script must be at least {min_words} words to ensure 15+ minutes of speaking time."

    try:
        # Call DeepSeek API (OpenAI-compatible)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional movie reviewer for YouTube. Write detailed, engaging reviews in a natural, conversational tone."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.8,
            "max_tokens": 8192,
            "stream": False,
        }

        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=120,  # Long timeout for script generation
        )

        if response.status_code == 200:
            data = response.json()
            script = data["choices"][0]["message"]["content"]
            word_count = len(script.split())

            print(f"Generated script: {word_count} words (target: {min_words}+ words)")

            if word_count < min_words:
                print(f"Warning: Script is shorter than target. Consider regenerating.")

            return script
        else:
            print(f"Error: DeepSeek API returned {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"Error generating script: {e}")
        return None


def generate_timestamps(script: str, language: str = None) -> str:
    """Generate timestamps for the video description."""
    language = language or CHANNEL_LANGUAGE

    # Split script into sections (by paragraphs or headers)
    paragraphs = [p.strip() for p in script.split("\n\n") if p.strip()]

    if not paragraphs:
        return ""

    # Estimate words per minute
    wpm = 150 if language == "vi" else 160
    timestamps = []
    current_time = 0  # in seconds

    # Add intro timestamp
    timestamps.append(f"0:00 - {'Giới thiệu' if language == 'vi' else 'Introduction'}")

    # Process each paragraph
    for i, para in enumerate(paragraphs):
        words = len(para.split())
        duration = (words / wpm) * 60  # in seconds
        current_time += duration

        # Add timestamp every ~2-3 minutes
        if i > 0 and i % 3 == 0:
            minutes = int(current_time // 60)
            seconds = int(current_time % 60)

            # Extract first few words as section title
            first_words = " ".join(para.split()[:5])
            if language == "vi":
                timestamp_text = f"{minutes}:{seconds:02d} - {first_words}..."
            else:
                timestamp_text = f"{minutes}:{seconds:02d} - {first_words}..."

            timestamps.append(timestamp_text)

    return "\n".join(timestamps)


def generate_title(movie: MovieData, language: str = None) -> str:
    """Generate SEO-optimized title for YouTube."""
    language = language or CHANNEL_LANGUAGE

    from config import REVIEW_TEMPLATES
    template = REVIEW_TEMPLATES[language]["series" if movie.is_series else "movie"]

    title = template["title_format"].format(
        title=movie.title,
        year=movie.year,
        tagline=movie.tagline or movie.original_title,
        season=movie.seasons,
        subtitle=movie.tagline or movie.original_title,
    )

    return title


def generate_description(movie: MovieData, script: str, language: str = None) -> str:
    """Generate SEO-optimized description for YouTube."""
    language = language or CHANNEL_LANGUAGE

    from config import REVIEW_TEMPLATES, CHANNEL_NAME
    template = REVIEW_TEMPLATES[language]["series" if movie.is_series else "movie"]

    # Generate timestamps
    timestamps = generate_timestamps(script, language)

    # Generate genre tags
    genre_tags = " ".join([g.replace(" ", "") for g in movie.genre_names[:3]])

    description = template["description_format"].format(
        title=movie.title,
        year=movie.year,
        overview=movie.overview[:500] + "..." if len(movie.overview) > 500 else movie.overview,
        rating=movie.rating,
        genres=", ".join(movie.genre_names),
        director=movie.director,
        cast=", ".join(movie.cast_names),
        timestamps=timestamps,
        tmdb_id=movie.tmdb_id,
        imdb_id=movie.imdb_id,
        genre_tags=genre_tags,
        channel_name=CHANNEL_NAME,
        season=movie.seasons,
        episodes=movie.episodes,
    )

    return description


def generate_tags(movie: MovieData, language: str = None) -> list[str]:
    """Generate tags for YouTube."""
    language = language or CHANNEL_LANGUAGE

    from config import REVIEW_TEMPLATES
    template = REVIEW_TEMPLATES[language]["series" if movie.is_series else "movie"]

    # Base tags
    tags = template["tags"].copy()

    # Add movie-specific tags
    tags.append(movie.title.lower())
    tags.append(f"{movie.title} {movie.year}")
    tags.extend([g.lower() for g in movie.genre_names])

    # Add director/actor tags if notable
    if movie.director:
        tags.append(movie.director.lower())

    # Add year tag
    tags.append(str(movie.year))

    # Remove duplicates
    tags = list(dict.fromkeys(tags))

    return tags[:30]  # YouTube limit


# ── Test Function ────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing script generator with DeepSeek API...")
    print(f"API Key set: {'Yes' if DEEPSEEK_API_KEY else 'No'}")

    if not DEEPSEEK_API_KEY:
        print("\nTo set up DeepSeek API:")
        print("1. Go to https://platform.deepseek.com")
        print("2. Sign up (free)")
        print("3. Get API key")
        print("4. Add to .env: DEEPSEEK_API_KEY=your_key")
        print("\nFree tier limits:")
        print("- 100,000 tokens/day")
        print("- No strict request limit")
        print("- Enough for 5-10 scripts/day")
