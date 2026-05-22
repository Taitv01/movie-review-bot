"""
Movie Review Bot - Video Builder
Assembles final video using MoviePy + FFmpeg.
"""

import os
import re
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy import (
    ImageClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    CompositeAudioClip,
)
from moviepy.video.fx import CrossFadeIn, CrossFadeOut
from movie_data import MovieData
from config import (
    VIDEOS_DIR,
    AUDIO_DIR,
    SUBTITLES_DIR,
    THUMBNAILS_DIR,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    MIN_VIDEO_DURATION,
    CHANNEL_LANGUAGE,
)


def build_video(
    movie: MovieData,
    audio_path: str,
    subtitle_path: str,
    thumbnail_path: str,
    language: str = None,
    background_images: list[str] = None,
) -> Optional[str]:
    """Build the final video from components."""
    language = language or CHANNEL_LANGUAGE

    output_path = str(VIDEOS_DIR / f"{movie.tmdb_id}_{language}.mp4")

    try:
        print(f"Building video for: {movie.title}")

        # Load audio
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration

        print(f"Audio duration: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")

        # Check minimum duration
        if audio_duration < MIN_VIDEO_DURATION:
            print(f"Warning: Audio is shorter than {MIN_VIDEO_DURATION/60} minutes")

        # Create video clips
        clips = []

        # 1. Intro clip (5 seconds)
        intro_clip = create_intro_clip(movie, language)
        clips.append(intro_clip)

        # 2. Main content clips with background images
        main_clips = create_main_content_clips(
            movie=movie,
            audio_path=audio_path,
            subtitle_path=subtitle_path,
            duration=audio_duration,
            background_images=background_images,
            language=language,
        )
        clips.extend(main_clips)

        # 3. Outro clip (10 seconds)
        outro_clip = create_outro_clip(language)
        clips.append(outro_clip)

        # Concatenate all clips
        final_clip = concatenate_videoclips(clips, method="compose")

        # Add audio
        final_clip = final_clip.with_audio(audio_clip)

        # Set duration
        final_clip = final_clip.with_duration(audio_clip.duration + 15)  # +15 for intro/outro

        # Export video
        print(f"Exporting video to: {output_path}")
        final_clip.write_videofile(
            output_path,
            fps=VIDEO_FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate="5000k",
            preset="medium",
            threads=4,
        )

        # Clean up
        audio_clip.close()
        final_clip.close()

        # Verify output
        if Path(output_path).exists():
            size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"Video created: {output_path} ({size_mb:.1f} MB)")
            return output_path

        return None

    except Exception as e:
        print(f"Error building video: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_intro_clip(movie: MovieData, language: str = "vi") -> ImageClip:
    """Create intro clip with movie title."""
    # Create intro image
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (20, 20, 40))
    draw = ImageDraw.Draw(img)

    # Add gradient background
    for y in range(VIDEO_HEIGHT):
        r = int(20 + (y / VIDEO_HEIGHT) * 30)
        g = int(10 + (y / VIDEO_HEIGHT) * 20)
        b = int(40 + (y / VIDEO_HEIGHT) * 40)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))

    # Add channel name
    from config import CHANNEL_NAME
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 72)
        subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
    except Exception:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Channel name
    text = CHANNEL_NAME
    text_bbox = draw.textbbox((0, 0), text, font=title_font)
    text_width = text_bbox[2] - text_bbox[0]
    x = (VIDEO_WIDTH - text_width) // 2
    y = VIDEO_HEIGHT // 3
    draw.text((x, y), text, font=title_font, fill=(255, 255, 255))

    # Movie title
    title = movie.title
    text_bbox = draw.textbbox((0, 0), title, font=subtitle_font)
    text_width = text_bbox[2] - text_bbox[0]
    x = (VIDEO_WIDTH - text_width) // 2
    y = VIDEO_HEIGHT // 2
    draw.text((x, y), title, font=subtitle_font, fill=(200, 200, 200))

    # Save temporary image
    temp_path = str(VIDEOS_DIR / "temp_intro.jpg")
    img.save(temp_path, "JPEG", quality=95)

    # Create clip
    clip = ImageClip(temp_path, duration=5)

    # Clean up temp file
    os.remove(temp_path)

    return clip


def create_main_content_clips(
    movie: MovieData,
    audio_path: str,
    subtitle_path: str,
    duration: float,
    background_images: list[str] = None,
    language: str = "vi",
) -> list:
    """Create main content clips with background images and subtitles."""
    clips = []

    # Load subtitles
    subtitles = load_subtitles(subtitle_path)

    if not subtitles:
        # Create a single long clip with thumbnail
        clip = create_single_content_clip(movie, duration, language)
        clips.append(clip)
        return clips

    # Create clips for each subtitle segment
    current_time = 0

    for i, (start_time, end_time, text) in enumerate(subtitles):
        # Calculate duration
        segment_duration = end_time - start_time

        if segment_duration <= 0:
            continue

        # Choose background image
        if background_images and i < len(background_images):
            bg_path = background_images[i % len(background_images)]
        else:
            bg_path = None

        # Create clip
        clip = create_subtitle_clip(
            text=text,
            duration=segment_duration,
            background_path=bg_path,
            movie=movie,
            language=language,
        )

        clips.append(clip)
        current_time = end_time

    return clips


def create_single_content_clip(movie: MovieData, duration: float, language: str = "vi") -> ImageClip:
    """Create a single long content clip."""
    # Create background
    if movie.poster_url:
        try:
            import requests
            response = requests.get(movie.poster_url, timeout=10)
            img = Image.open(requests.io.BytesIO(response.content)).convert("RGB")
            img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
        except Exception:
            img = create_gradient_background()
    else:
        img = create_gradient_background()

    # Add dark overlay
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 150))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")

    # Save temporary image
    temp_path = str(VIDEOS_DIR / "temp_content.jpg")
    img.save(temp_path, "JPEG", quality=95)

    # Create clip
    clip = ImageClip(temp_path, duration=duration)

    # Clean up
    os.remove(temp_path)

    return clip


def create_subtitle_clip(
    text: str,
    duration: float,
    background_path: str = None,
    movie: MovieData = None,
    language: str = "vi",
) -> ImageClip:
    """Create a clip with subtitle text."""
    # Create or load background
    if background_path and Path(background_path).exists():
        img = Image.open(background_path).convert("RGB")
        img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
    else:
        img = create_gradient_background()

    # Add dark overlay
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 180))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")

    # Add subtitle text
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
    except Exception:
        font = ImageFont.load_default()

    # Word wrap text
    wrapped_text = word_wrap(text, max_chars=50)

    # Position at bottom third
    text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_height = text_bbox[3] - text_bbox[1]
    x = VIDEO_WIDTH // 2
    y = VIDEO_HEIGHT - text_height - 100

    # Draw text with outline
    outline_color = (0, 0, 0)
    text_color = (255, 255, 255)

    # Outline
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
        draw.text((x + dx, y + dy), wrapped_text, font=font, fill=outline_color, anchor="mm")

    # Main text
    draw.text((x, y), wrapped_text, font=font, fill=text_color, anchor="mm")

    # Save temporary image
    temp_path = str(VIDEOS_DIR / f"temp_subtitle_{hash(text) % 10000}.jpg")
    img.save(temp_path, "JPEG", quality=95)

    # Create clip
    clip = ImageClip(temp_path, duration=duration)

    # Clean up
    os.remove(temp_path)

    return clip


def create_outro_clip(language: str = "vi") -> ImageClip:
    """Create outro clip with CTA."""
    # Create outro image
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (20, 20, 40))
    draw = ImageDraw.Draw(img)

    # Add gradient background
    for y in range(VIDEO_HEIGHT):
        r = int(20 + (y / VIDEO_HEIGHT) * 30)
        g = int(10 + (y / VIDEO_HEIGHT) * 20)
        b = int(40 + (y / VIDEO_HEIGHT) * 40)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))

    # Add CTA text
    from config import CHANNEL_NAME
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()

    # CTA text
    if language == "vi":
        cta_lines = [
            "Cảm ơn các bạn đã xem!",
            "",
            "Đừng quên LIKE, SHARE",
            "và SUBSCRIBE nhé!",
            "",
            CHANNEL_NAME,
        ]
    else:
        cta_lines = [
            "Thanks for watching!",
            "",
            "Don't forget to LIKE, SHARE",
            "and SUBSCRIBE!",
            "",
            CHANNEL_NAME,
        ]

    y_start = VIDEO_HEIGHT // 4
    for i, line in enumerate(cta_lines):
        if not line:
            continue
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (VIDEO_WIDTH - text_width) // 2
        y = y_start + i * 60
        draw.text((x, y), line, font=font, fill=(255, 255, 255))

    # Save temporary image
    temp_path = str(VIDEOS_DIR / "temp_outro.jpg")
    img.save(temp_path, "JPEG", quality=95)

    # Create clip
    clip = ImageClip(temp_path, duration=10)

    # Clean up
    os.remove(temp_path)

    return clip


def load_subtitles(srt_path: str) -> list[tuple]:
    """Load SRT subtitles."""
    if not Path(srt_path).exists():
        return []

    subtitles = []

    try:
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse SRT format
        pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            index, start, end, text = match
            start_time = parse_timestamp(start)
            end_time = parse_timestamp(end)
            text = text.strip()
            subtitles.append((start_time, end_time, text))

    except Exception as e:
        print(f"Error loading subtitles: {e}")

    return subtitles


def parse_timestamp(timestamp: str) -> float:
    """Parse SRT timestamp to seconds."""
    parts = timestamp.replace(",", ".").split(":")
    hours, minutes, seconds = int(parts[0]), int(parts[1]), float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def create_gradient_background() -> Image.Image:
    """Create a gradient background."""
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    for y in range(VIDEO_HEIGHT):
        r = int(20 + (y / VIDEO_HEIGHT) * 30)
        g = int(10 + (y / VIDEO_HEIGHT) * 20)
        b = int(40 + (y / VIDEO_HEIGHT) * 40)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))

    return img


def word_wrap(text: str, max_chars: int = 50) -> str:
    """Wrap text to fit within max_chars per line."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + (1 if current_line else 0) > max_chars:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                lines.append(word)
                current_line = []
                current_length = 0
        else:
            current_line.append(word)
            current_length += len(word) + (1 if len(current_line) > 1 else 0)

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


# ── Test Function ────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing video builder...")

    # Create a mock movie data
    movie = MovieData(
        tmdb_id=12345,
        title="Test Movie Title",
        year=2026,
        rating=8.5,
        genre_names=["Action", "Drama"],
    )

    # Test intro clip
    print("\nCreating intro clip...")
    intro = create_intro_clip(movie, "vi")
    print(f"Intro duration: {intro.duration}s")

    # Test outro clip
    print("\nCreating outro clip...")
    outro = create_outro_clip("vi")
    print(f"Outro duration: {outro.duration}s")

    print("\nVideo builder components tested successfully!")
