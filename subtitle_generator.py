"""
Movie Review Bot - Subtitle Generator
Generates SRT subtitles from script text.
No Whisper needed - we already have the script text.
"""

import re
from pathlib import Path
from typing import Optional
from config import SUBTITLES_DIR, CHANNEL_LANGUAGE, WORDS_PER_MINUTE


def generate_subtitles(
    script: str,
    movie_id: int,
    language: str = None,
    words_per_subtitle: int = 8,
    max_chars_per_line: int = 42,
) -> Optional[str]:
    """Generate SRT subtitles from script text."""
    language = language or CHANNEL_LANGUAGE

    # Clean script
    clean_text = clean_script_for_subtitles(script)

    # Split into sentences
    sentences = split_into_sentences(clean_text)

    if not sentences:
        print("Error: No sentences found in script")
        return None

    # Calculate timing
    wpm = WORDS_PER_MINUTE[language]
    subtitle_entries = []
    current_time = 0.0  # in seconds
    subtitle_index = 1

    for sentence in sentences:
        words = sentence.split()
        if not words:
            continue

        # Split long sentences into chunks
        chunks = split_sentence_into_chunks(sentence, words_per_subtitle, max_chars_per_line)

        for chunk in chunks:
            # Calculate duration based on word count
            word_count = len(chunk.split())
            duration = (word_count / wpm) * 60

            # Add small pause between subtitles
            pause = 0.2

            # Format timestamps
            start_time = format_timestamp(current_time)
            end_time = format_timestamp(current_time + duration)

            # Add subtitle entry
            subtitle_entries.append(
                f"{subtitle_index}\n"
                f"{start_time} --> {end_time}\n"
                f"{chunk}\n"
            )

            current_time += duration + pause
            subtitle_index += 1

    # Write SRT file
    output_path = str(SUBTITLES_DIR / f"{movie_id}_{language}.srt")
    srt_content = "\n".join(subtitle_entries)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        print(f"Subtitles generated: {output_path}")
        print(f"Total entries: {subtitle_index - 1}")
        print(f"Estimated duration: {format_timestamp(current_time)}")

        return output_path
    except Exception as e:
        print(f"Error writing subtitles: {e}")
        return None


def clean_script_for_subtitles(script: str) -> str:
    """Clean script text for subtitle generation."""
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', script, flags=re.MULTILINE)

    # Remove markdown bold/italic
    text = re.sub(r'\*{1,2}(.+?)\*{1,2}', r'\1', text)

    # Remove markdown links
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

    # Remove markdown lists
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Clean up
    text = text.strip()

    return text


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Split by common sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Clean up
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def split_sentence_into_chunks(
    sentence: str,
    words_per_chunk: int = 8,
    max_chars_per_line: int = 42,
) -> list[str]:
    """Split a sentence into subtitle-sized chunks."""
    words = sentence.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        # Check if adding this word would exceed limits
        new_length = current_length + len(word) + (1 if current_chunk else 0)

        if len(current_chunk) >= words_per_chunk or new_length > max_chars_per_line:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                # Word is too long, add it anyway
                chunks.append(word)
                current_chunk = []
                current_length = 0
        else:
            current_chunk.append(word)
            current_length = new_length

    # Add remaining chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def adjust_subtitle_timing(srt_path: str, offset_seconds: float) -> bool:
    """Adjust all timestamps in an SRT file by an offset."""
    try:
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse and adjust timestamps
        def adjust_timestamp(match):
            timestamp = match.group(0)
            parts = timestamp.replace(",", ".").split(":")
            hours, minutes, seconds = int(parts[0]), int(parts[1]), float(parts[2])
            total_seconds = hours * 3600 + minutes * 60 + seconds + offset_seconds
            return format_timestamp(total_seconds)

        # Adjust timestamps
        adjusted = re.sub(
            r'\d{2}:\d{2}:\d{2},\d{3}',
            adjust_timestamp,
            content
        )

        # Write back
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(adjusted)

        return True
    except Exception as e:
        print(f"Error adjusting subtitles: {e}")
        return False


# ── Test Function ────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing subtitle generator...")

    # Test with a sample script
    test_script = """
Xin chào các bạn! Hôm nay tôi sẽ review bộ phim mới nhất của đạo diễn nổi tiếng.

Bộ phim này kể về một câu chuyện cảm động về tình bạn và sự hy sinh. Diễn viên chính đã thể hiện rất xuất sắc vai diễn của mình.

Điểm tôi thích nhất ở bộ phim này là cách đạo diễn xây dựng các tình tiết. Mỗi cảnh quay đều có ý nghĩa và góp phần phát triển câu chuyện.

Tuy nhiên, phim cũng có một số điểm yếu. Nhịp phim hơi chậm ở giữa, và một số tình tiết chưa được giải thích rõ ràng.

Tổng thể, tôi đánh giá bộ phim này 8/10. Đây là một bộ phim đáng xem và tôi highly recommend cho mọi người.
"""

    print(f"\nTest script ({len(test_script.split())} words):")
    print(test_script[:200] + "...")

    # Generate subtitles
    output_path = generate_subtitles(
        script=test_script,
        movie_id=12345,
        language="vi",
        words_per_subtitle=8,
        max_chars_per_line=42,
    )

    if output_path:
        # Read and display first few entries
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"\nGenerated SRT file ({output_path}):")
        print(content[:500])
    else:
        print("\nFailed to generate subtitles")
