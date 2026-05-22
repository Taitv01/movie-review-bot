"""
Movie Review Bot - Voice Generator
Uses Microsoft Edge TTS (free) to generate audio from scripts.
"""

import asyncio
import edge_tts
from pathlib import Path
from typing import Optional
from config import AUDIO_DIR, VOICES, CHANNEL_LANGUAGE, DEFAULT_VOICE


async def generate_audio_async(
    text: str,
    output_path: str,
    voice: str = None,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> bool:
    """Generate audio from text using edge-tts (async)."""
    voice = voice or DEFAULT_VOICE

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Error generating audio: {e}")
        return False


def generate_audio(
    text: str,
    output_path: str,
    voice: str = None,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> bool:
    """Generate audio from text using edge-tts (sync wrapper)."""
    return asyncio.run(generate_audio_async(text, output_path, voice, rate, volume, pitch))


def generate_movie_audio(
    script: str,
    movie_id: int,
    language: str = None,
    voice: str = None,
    rate: str = "-5%",  # Slightly slower for clarity
) -> Optional[str]:
    """Generate audio for a movie review script."""
    language = language or CHANNEL_LANGUAGE
    voice = voice or VOICES[language]["female"]

    # Clean script text (remove markdown, etc.)
    clean_text = clean_script(script)

    # Output path
    output_path = str(AUDIO_DIR / f"{movie_id}_{language}.mp3")

    print(f"Generating audio with voice: {voice}")
    print(f"Text length: {len(clean_text)} characters")

    success = generate_audio(
        text=clean_text,
        output_path=output_path,
        voice=voice,
        rate=rate,
    )

    if success:
        # Check file size
        audio_path = Path(output_path)
        if audio_path.exists():
            size_mb = audio_path.stat().st_size / (1024 * 1024)
            print(f"Audio generated: {output_path} ({size_mb:.1f} MB)")
            return output_path

    return None


def clean_script(script: str) -> str:
    """Clean script text for TTS."""
    import re

    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', script, flags=re.MULTILINE)

    # Remove markdown bold/italic
    text = re.sub(r'\*{1,2}(.+?)\*{1,2}', r'\1', text)

    # Remove markdown links
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

    # Remove markdown lists
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)

    # Remove extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Clean up
    text = text.strip()

    return text


def get_available_voices(language: str = None) -> list[dict]:
    """Get list of available voices for a language."""
    language = language or CHANNEL_LANGUAGE

    async def _get_voices():
        voices = await edge_tts.list_voices()
        return [v for v in voices if v["Locale"].startswith(language)]

    return asyncio.run(_get_voices())


def list_voices(language: str = None) -> None:
    """Print available voices for a language."""
    language = language or CHANNEL_LANGUAGE
    voices = get_available_voices(language)

    print(f"\nAvailable voices for '{language}':")
    print("-" * 60)
    for voice in voices:
        print(f"  {voice['ShortName']}: {voice['Gender']} - {voice['FriendlyName']}")
    print(f"\nTotal: {len(voices)} voices")


# ── Test Function ────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing voice generator...")

    # Test with a short text
    test_text = "Xin chào! Đây là bài review phim hôm nay. Hãy cùng tôi khám phá bộ phim này nhé!"
    test_path = str(AUDIO_DIR / "test_audio.mp3")

    print(f"\nGenerating test audio...")
    print(f"Text: {test_text}")
    print(f"Voice: {DEFAULT_VOICE}")

    success = generate_audio(
        text=test_text,
        output_path=test_path,
        voice=DEFAULT_VOICE,
        rate="-5%",
    )

    if success:
        print(f"\nSuccess! Audio saved to: {test_path}")

        # List available voices
        list_voices()
    else:
        print("\nFailed to generate audio")
