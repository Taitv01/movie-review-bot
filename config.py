"""
Movie Review Bot - Configuration
All API keys are loaded from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Paths ────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
AUDIO_DIR = OUTPUT_DIR / "audio"
SUBTITLES_DIR = OUTPUT_DIR / "subtitles"
THUMBNAILS_DIR = OUTPUT_DIR / "thumbnails"
VIDEOS_DIR = OUTPUT_DIR / "videos"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
TEMPLATES_DIR = ASSETS_DIR / "templates"

# Create directories if they don't exist
for d in [AUDIO_DIR, SUBTITLES_DIR, THUMBNAILS_DIR, VIDEOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── API Keys ─────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")
YOUTUBE_CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")

# ── Channel Settings ─────────────────────────────────────────
CHANNEL_LANGUAGE = os.getenv("CHANNEL_LANGUAGE", "vi")  # vi or en
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "PhimHay Review")

# ── Voice Settings ───────────────────────────────────────────
VOICES = {
    "vi": {
        "female": "vi-VN-HoaiMyNeural",
        "male": "vi-VN-NamMinhNeural",
    },
    "en": {
        "female": "en-US-JennyNeural",
        "male": "en-US-GuyNeural",
    },
}

DEFAULT_VOICE = VOICES[CHANNEL_LANGUAGE]["female"]

# ── Video Settings ───────────────────────────────────────────
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
MIN_VIDEO_DURATION = 15 * 60  # 15 minutes in seconds

# ── Script Settings ──────────────────────────────────────────
# Words per minute for speech rate estimation
WORDS_PER_MINUTE = {
    "vi": 150,  # Vietnamese is spoken slower
    "en": 160,  # English average
}

# Minimum word count for 15+ minute video
MIN_WORD_COUNT = {
    "vi": 2500,
    "en": 2000,
}

# ── TMDB Settings ────────────────────────────────────────────
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"
POSTER_SIZE = "w500"       # For thumbnails
BACKDROP_SIZE = "original" # For video backgrounds

# ── YouTube Settings ─────────────────────────────────────────
YOUTUBE_CATEGORY_ID = "24"  # Entertainment
YOUTUBE_PRIVACY = "public"  # public, private, or unlisted

# ── Content Templates ────────────────────────────────────────
REVIEW_TEMPLATES = {
    "vi": {
        "movie": {
            "title_format": "REVIEW {title} - {tagline} | {year}",
            "description_format": """🎬 REVIEW PHIM: {title} ({year})

📋 Nội dung:
{overview}

⭐ Đánh giá: {rating}/10
🎭 Thể loại: {genres}
🎬 Đạo diễn: {director}
🌟 Diễn viên: {cast}

📌 Timestamps:
0:00 - Giới thiệu
{timestamps}

🔗 Liên kết:
- TMDB: https://www.themoviedb.org/movie/{tmdb_id}
- IMDB: https://www.imdb.com/title/{imdb_id}

#reviewphim #{genre_tags} #phim{year}

---
© {channel_name} - Đừng quên Like, Share và Subscribe!
""",
            "tags": ["review phim", "phim hay", "đánh giá phim", "phim mới", "movie review"],
        },
        "series": {
            "title_format": "REVIEW {title} Season {season} - {subtitle} | {year}",
            "description_format": """🎬 REVIEW PHIM BỘ: {title} Season {season} ({year})

📋 Nội dung:
{overview}

⭐ Đánh giá: {rating}/10
🎭 Thể loại: {genres}
📺 Số tập: {episodes}
🎬 Đạo diễn: {director}

📌 Timestamps:
0:00 - Giới thiệu
{timestamps}

🔗 Liên kết:
- TMDB: https://www.themoviedb.org/tv/{tmdb_id}

#reviewphimbo #{genre_tags} #phimbo{year}

---
© {channel_name} - Đừng quên Like, Share và Subscribe!
""",
            "tags": ["review phim bộ", "phim bộ hay", "phim dài tập", "series review", "drama"],
        },
    },
    "en": {
        "movie": {
            "title_format": "{title} ({year}) - Movie Review | {tagline}",
            "description_format": """🎬 MOVIE REVIEW: {title} ({year})

📋 Summary:
{overview}

⭐ Rating: {rating}/10
🎭 Genre: {genres}
🎬 Director: {director}
🌟 Cast: {cast}

📌 Timestamps:
0:00 - Introduction
{timestamps}

🔗 Links:
- TMDB: https://www.themoviedb.org/movie/{tmdb_id}
- IMDB: https://www.imdb.com/title/{imdb_id}

#moviereview #{genre_tags} #film{year}

---
© {channel_name} - Don't forget to Like, Share and Subscribe!
""",
            "tags": ["movie review", "film review", "new movies", "movie recap", "movie analysis"],
        },
        "series": {
            "title_format": "{title} Season {season} Review - {subtitle} | {year}",
            "description_format": """🎬 TV SERIES REVIEW: {title} Season {season} ({year})

📋 Summary:
{overview}

⭐ Rating: {rating}/10
🎭 Genre: {genres}
📺 Episodes: {episodes}
🎬 Creator: {director}

📌 Timestamps:
0:00 - Introduction
{timestamps}

🔗 Links:
- TMDB: https://www.themoviedb.org/tv/{tmdb_id}

#tvseries #{genre_tags} #series{year}

---
© {channel_name} - Don't forget to Like, Share and Subscribe!
""",
            "tags": ["tv series review", "series recap", "season review", "tv show review", "drama review"],
        },
    },
}

# ── AI Prompt Templates ──────────────────────────────────────
SCRIPT_PROMPTS = {
    "vi": {
        "movie": """Bạn là một reviewer phim chuyên nghiệp trên YouTube. Hãy viết bài review phim sau bằng tiếng Việt.

THÔNG TIN PHIM:
- Tên phim: {title} ({year})
- Thể loại: {genres}
- Đạo diễn: {director}
- Diễn viên chính: {cast}
- Đánh giá TMDB: {rating}/10
- Nội dung: {overview}

YÊU CẦU:
1. Bài review phải dài ít nhất 2500 từ (tương đương 15+ phút nói)
2. Giọng văn tự nhiên, như đang nói chuyện với người xem
3. Cấu trúc:
   - Phần mở đầu: Hook hấp dẫn, giới thiệu phim
   - Phần nội dung: Phân tích cốt truyện, diễn xuất, kỹ thuật quay
   - Phần đánh giá: Đưa ra nhận xét công bằng
   - Phần kết: Tổng kết, đề xuất xem hay không
4. KHÔNG spoil quá nhiều nội dung phim
5. Thêm cảm xúc, câu hỏi tu từ để thu hút người xem
6. Đề cập đến điểm mạnh và điểm yếu của phim

Hãy viết bài review đầy đủ, chi tiết, và hấp dẫn.""",

        "series": """Bạn là một reviewer phim bộ chuyên nghiệp trên YouTube. Hãy viết bài review phim bộ sau bằng tiếng Việt.

THÔNG TIN PHIM BỘ:
- Tên phim: {title} ({year})
- Season: {season}
- Số tập: {episodes}
- Thể loại: {genres}
- Đạo diễn: {director}
- Đánh giá TMDB: {rating}/10
- Nội dung: {overview}

YÊU CẦU:
1. Bài review phải dài ít nhất 2500 từ (tương đương 15+ phút nói)
2. Giọng văn tự nhiên, như đang nói chuyện với người xem
3. Cấu trúc:
   - Phần mở đầu: Hook hấp dẫn, giới thiệu phim bộ
   - Phần tóm tắt: Tóm tắt nội dung từng tập (không spoil quá nhiều)
   - Phần phân tích: Nhân vật, mối quan hệ, plot twist
   - Phần đánh giá: Đánh giá tổng thể season
   - Phần dự đoán: Dự đoán cho season tiếp theo
4. Phân tích sự phát triển của nhân vật qua các tập
5. Đề cập đến những khoảnh khắc ấn tượng nhất
6. So sánh với các phim bộ khác nếu có thể

Hãy viết bài review đầy đủ, chi tiết, và hấp dẫn.""",
    },
    "en": {
        "movie": """You are a professional movie reviewer on YouTube. Write a detailed movie review in English.

MOVIE INFO:
- Title: {title} ({year})
- Genre: {genres}
- Director: {director}
- Cast: {cast}
- TMDB Rating: {rating}/10
- Overview: {overview}

REQUIREMENTS:
1. The review must be at least 2000 words (equivalent to 15+ minutes of speaking)
2. Natural, conversational tone - like talking to viewers
3. Structure:
   - Opening: Hook, introduce the movie
   - Content: Plot analysis, acting, cinematography
   - Evaluation: Fair assessment
   - Conclusion: Summary, recommendation
4. Don't spoil too much of the plot
5. Add emotions, rhetorical questions to engage viewers
6. Discuss strengths and weaknesses

Write a complete, detailed, and engaging review.""",

        "series": """You are a professional TV series reviewer on YouTube. Write a detailed series review in English.

SERIES INFO:
- Title: {title} ({year})
- Season: {season}
- Episodes: {episodes}
- Genre: {genres}
- Creator: {director}
- TMDB Rating: {rating}/10
- Overview: {overview}

REQUIREMENTS:
1. The review must be at least 2000 words (equivalent to 15+ minutes of speaking)
2. Natural, conversational tone - like talking to viewers
3. Structure:
   - Opening: Hook, introduce the series
   - Summary: Episode breakdown (no major spoilers)
   - Analysis: Characters, relationships, plot twists
   - Evaluation: Overall season assessment
   - Predictions: Theories for next season
4. Analyze character development throughout episodes
5. Highlight the most impactful moments
6. Compare with similar series if possible

Write a complete, detailed, and engaging review.""",
    },
}
