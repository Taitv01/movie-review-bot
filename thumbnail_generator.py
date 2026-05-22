"""
Movie Review Bot - Thumbnail Generator
Creates YouTube thumbnails using Pillow + TMDB posters.
"""

import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from typing import Optional
from movie_data import MovieData
from config import THUMBNAILS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT


# YouTube thumbnail standard size
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720


def generate_thumbnail(
    movie: MovieData,
    output_path: str = None,
    language: str = "vi",
) -> Optional[str]:
    """Generate a YouTube thumbnail for a movie review."""
    if output_path is None:
        output_path = str(THUMBNAILS_DIR / f"{movie.tmdb_id}_{language}.jpg")

    try:
        # Download movie poster or backdrop
        background = download_movie_image(movie)

        if background is None:
            # Create gradient background as fallback
            background = create_gradient_background()

        # Resize to thumbnail size
        background = background.resize((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), Image.Resampling.LANCZOS)

        # Enhance the image
        background = enhance_image(background)

        # Add dark overlay for text readability
        background = add_dark_overlay(background)

        # Add text overlays
        draw = ImageDraw.Draw(background)

        # Add movie title
        add_title_text(draw, movie.title, language)

        # Add rating badge
        add_rating_badge(draw, movie.rating, language)

        # Add "REVIEW" text
        add_review_text(draw, language)

        # Add channel branding
        add_channel_branding(draw, language)

        # Save thumbnail
        background.save(output_path, "JPEG", quality=95)

        print(f"Thumbnail generated: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None


def download_movie_image(movie: MovieData) -> Optional[Image.Image]:
    """Download movie poster or backdrop from TMDB."""
    # Try backdrop first (better for landscape)
    if movie.backdrop_url:
        try:
            response = requests.get(movie.backdrop_url, timeout=10)
            response.raise_for_status()
            return Image.open(requests.io.BytesIO(response.content)).convert("RGB")
        except Exception:
            pass

    # Try poster
    if movie.poster_url:
        try:
            response = requests.get(movie.poster_url, timeout=10)
            response.raise_for_status()
            return Image.open(requests.io.BytesIO(response.content)).convert("RGB")
        except Exception:
            pass

    return None


def create_gradient_background() -> Image.Image:
    """Create a gradient background."""
    image = Image.new("RGB", (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
    draw = ImageDraw.Draw(image)

    # Dark gradient
    for y in range(THUMBNAIL_HEIGHT):
        r = int(20 + (y / THUMBNAIL_HEIGHT) * 30)
        g = int(10 + (y / THUMBNAIL_HEIGHT) * 20)
        b = int(40 + (y / THUMBNAIL_HEIGHT) * 40)
        draw.line([(0, y), (THUMBNAIL_WIDTH, y)], fill=(r, g, b))

    return image


def enhance_image(image: Image.Image) -> Image.Image:
    """Enhance image for thumbnail."""
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.3)

    # Increase saturation
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.2)

    # Slightly brighten
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)

    return image


def add_dark_overlay(image: Image.Image) -> Image.Image:
    """Add dark overlay for text readability."""
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 120))
    image = image.convert("RGBA")
    image = Image.alpha_composite(image, overlay)
    return image.convert("RGB")


def add_title_text(draw: ImageDraw.Draw, title: str, language: str) -> None:
    """Add movie title to thumbnail."""
    # Try to load a font, fallback to default
    try:
        # Try system fonts
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        font = None
        for path in font_paths:
            if Path(path).exists():
                font = ImageFont.truetype(path, 48)
                break
        if font is None:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Truncate title if too long
    max_chars = 30
    display_title = title[:max_chars] + "..." if len(title) > max_chars else title

    # Position
    x = 50
    y = 300

    # Draw text with outline
    outline_color = (0, 0, 0)
    text_color = (255, 255, 255)

    # Outline
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
        draw.text((x + dx, y + dy), display_title, font=font, fill=outline_color)

    # Main text
    draw.text((x, y), display_title, font=font, fill=text_color)


def add_rating_badge(draw: ImageDraw.Draw, rating: float, language: str) -> None:
    """Add rating badge to thumbnail."""
    # Rating text
    rating_text = f"{rating}/10"

    # Try to load font
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
    except Exception:
        font = ImageFont.load_default()

    # Badge background
    badge_x = THUMBNAIL_WIDTH - 200
    badge_y = 50
    badge_width = 150
    badge_height = 60

    # Draw badge background (yellow/gold)
    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)],
        radius=10,
        fill=(255, 200, 0),
    )

    # Draw rating text
    text_x = badge_x + 20
    text_y = badge_y + 10
    draw.text((text_x, text_y), rating_text, font=font, fill=(0, 0, 0))


def add_review_text(draw: ImageDraw.Draw, language: str) -> None:
    """Add 'REVIEW' text to thumbnail."""
    review_text = "REVIEW" if language == "en" else "REVIEW PHIM"

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 64)
    except Exception:
        font = ImageFont.load_default()

    # Position
    x = 50
    y = 100

    # Draw with red background
    text_bbox = draw.textbbox((x, y), review_text, font=font)
    padding = 15
    draw.rounded_rectangle(
        [(text_bbox[0] - padding, text_bbox[1] - padding),
         (text_bbox[2] + padding, text_bbox[3] + padding)],
        radius=10,
        fill=(255, 0, 0),
    )

    # Draw text
    draw.text((x, y), review_text, font=font, fill=(255, 255, 255))


def add_channel_branding(draw: ImageDraw.Draw, language: str) -> None:
    """Add channel name/branding."""
    from config import CHANNEL_NAME

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()

    # Position at bottom right
    text = CHANNEL_NAME
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]

    x = THUMBNAIL_WIDTH - text_width - 30
    y = THUMBNAIL_HEIGHT - 40

    draw.text((x, y), text, font=font, fill=(200, 200, 200))


# ── Test Function ────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing thumbnail generator...")

    # Create a mock movie data
    movie = MovieData(
        tmdb_id=12345,
        title="Test Movie Title",
        year=2026,
        rating=8.5,
        genre_names=["Action", "Drama"],
    )

    # Generate thumbnail
    output_path = generate_thumbnail(movie, language="vi")

    if output_path:
        print(f"\nThumbnail saved to: {output_path}")

        # Open and display info
        img = Image.open(output_path)
        print(f"Size: {img.size}")
        print(f"Mode: {img.mode}")
    else:
        print("\nFailed to generate thumbnail")
