# Movie Review Bot 🎬

Tự động tạo video review phim YouTube sử dụng AI. 100% miễn phí.

## Tính năng

- ✅ Tự động fetch phim trending từ TMDB
- ✅ Tạo script review bằng DeepSeek AI (miễn phí, 100K tokens/day)
- ✅ Tạo audio bằng Edge TTS (miễn phí, giọng tự nhiên)
- ✅ Tạo phụ đề SRT từ script
- ✅ Tạo thumbnail tự động
- ✅ Ghép video tự động (FFmpeg + MoviePy)
- ✅ Upload lên YouTube tự động
- ✅ Hỗ trợ tiếng Việt và tiếng Anh
- ✅ Chạy tự động qua GitHub Actions

## Tech Stack (100% Miễn phí)

| Component | Tool | Cost |
|-----------|------|------|
| Script AI | DeepSeek API | $0 |
| Voice | Edge TTS | $0 |
| Video | FFmpeg + MoviePy | $0 |
| Thumbnails | Pillow + TMDB | $0 |
| Movie Data | TMDB API | $0 |
| Upload | YouTube Data API v3 | $0 |
| Scheduling | GitHub Actions | $0 |

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/yourusername/movie-review-bot.git
cd movie-review-bot
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cài đặt FFmpeg

**Windows:**
```bash
choco install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### 4. Lấy API Keys (miễn phí)

#### DeepSeek API
1. Vào https://platform.deepseek.com
2. Đăng ký tài khoản (miễn phí)
3. Vào API Keys section
4. Copy API key

#### TMDB API
1. Vào https://www.themoviedb.org
2. Đăng ký tài khoản
3. Vào Settings → API
4. Copy API key

#### OMDB API (tùy chọn)
1. Vào http://www.omdbapi.com/apikey.aspx
2. Đăng ký API key miễn phí
3. Copy API key

#### YouTube API
1. Vào https://console.cloud.google.com
2. Tạo project mới
3. Enable YouTube Data API v3
4. Tạo OAuth2 credentials (Desktop app)
5. Download client_secret.json

### 5. Cấu hình .env

```bash
cp .env.example .env
```

Edit `.env` và điền API keys:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
TMDB_API_KEY=your_tmdb_api_key
OMDB_API_KEY=your_omdb_api_key
CHANNEL_LANGUAGE=vi
CHANNEL_NAME=PhimHay Review
```

## Sử dụng

### Chạy 1 phim cụ thể

```bash
python pipeline.py --movie-id 550 --language vi
```

### Chạy trending movies

```bash
python pipeline.py --trending --count 1 --language vi
```

### Upload lên YouTube

```bash
python pipeline.py --trending --count 1 --upload --privacy public
```

### Chạy với TV series

```bash
python pipeline.py --movie-id 1399 --type tv --language en
```

## Tự động hóa (GitHub Actions)

### 1. Setup GitHub Secrets

Vào repository → Settings → Secrets and variables → Actions

Thêm các secrets:

| Secret | Value |
|--------|-------|
| `DEEPSEEK_API_KEY` | DeepSeek API key |
| `TMDB_API_KEY` | TMDB API key |
| `OMDB_API_KEY` | OMDB API key |
| `YOUTUBE_CLIENT_SECRET` | Nội dung client_secret.json |
| `CHANNEL_LANGUAGE` | vi hoặc en |
| `CHANNEL_NAME` | Tên kênh YouTube |

### 2. Chạy tự động

Workflow sẽ tự chạy:
- **Lịch**: Thứ 4 và Chủ nhật, 10:00 AM UTC
- **Hoặc**: Chạy manual từ GitHub Actions tab

## Cấu trúc thư mục

```
movie-review-bot/
├── config.py              # Cấu hình
├── movie_data.py          # Fetch dữ liệu phim
├── script_generator.py    # Tạo script bằng AI
├── voice_generator.py     # Tạo audio
├── subtitle_generator.py  # Tạo phụ đề
├── thumbnail_generator.py # Tạo thumbnail
├── video_builder.py       # Ghép video
├── youtube_uploader.py    # Upload YouTube
├── pipeline.py            # Pipeline chính
├── requirements.txt       # Dependencies
├── .env                   # API keys (gitignored)
├── .github/workflows/     # GitHub Actions
├── assets/                # Fonts, templates, music
└── output/                # Videos, audio, subtitles
```

## Video Output

- **Độ phân giải**: 1920x1080 (Full HD)
- **Độ dài**: 15+ phút (đủ điều kiện monetize)
- **Format**: MP4 (H.264 + AAC)
- **FPS**: 30

## Monetization

### YouTube Partner Program
- **Yêu cầu**: 1,000 subs + 4,000 watch hours
- **Timeline**: 3-6 tháng với upload đều đặn
- **Revenue**: $3-10/1,000 views

### Affiliate Marketing
- Streaming services: Netflix, Disney+, Amazon Prime
- Movie merchandise: Amazon affiliate

## Chi phí

**$0** - Tất cả tools đều miễn phí:
- DeepSeek API: Free tier (100K tokens/day, ~5-10 scripts/day)
- Edge TTS: Completely free
- FFmpeg + MoviePy: Open source
- TMDB API: Free
- YouTube API: Free (6 uploads/day)
- GitHub Actions: Free (2,000 min/month)

## Troubleshooting

### "FFmpeg not found"
Cài đặt FFmpeg và thêm vào PATH.

### "DEEPSEEK_API_KEY not set"
Kiểm tra file `.env` đã có API key chưa.

### "Video too short"
Tăng MIN_WORD_COUNT trong config.py.

### "Upload failed"
Kiểm tra client_secret.json và YouTube API quota.

## License

MIT License

## Support

Issues và pull requests welcome!
