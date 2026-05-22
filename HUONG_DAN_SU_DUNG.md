# Hướng dẫn sử dụng Auto Review YouTube

## Tổng quan

Hệ thống tự động tạo video review phim YouTube sử dụng AI. 100% miễn phí.

**Tech Stack:**
- Script AI: DeepSeek API (miễn phí, 100K tokens/day)
- Voice: Edge TTS (miễn phí, giọng tự nhiên)
- Movie Data: OMDB API (miễn phí, 1,000 requests/day, cho phép thương mại)
- Video: FFmpeg + MoviePy (miễn phí)
- Subtitles: SRT generation (từ script)
- Thumbnails: Pillow + OMDB posters

---

## API Keys

### 1. DeepSeek API (Bắt buộc)
- **URL:** https://platform.deepseek.com
- **Giá:** Miễn phí (100K tokens/day)
- **Công dụng:** Tạo script review phim
- **Cách lấy:**
  1. Truy cập https://platform.deepseek.com
  2. Đăng ký tài khoản
  3. Vào API Keys section
  4. Copy API key

### 2. OMDB API (Bắt buộc)
- **URL:** http://www.omdbapi.com/apikey.aspx
- **Giá:** Miễn phí (1,000 requests/day)
- **Công dụng:** Lấy thông tin phim, rating, poster
- **Cho phép thương mại:** Có
- **Cách lấy:**
  1. Truy cập http://www.omdbapi.com/apikey.aspx
  2. Nhập email
  3. Kiểm tra email để kích hoạt key
  4. Copy API key

### 3. TMDB API (Tùy chọn)
- **URL:** https://www.themoviedb.org/settings/api
- **Giá:** Miễn phí (phi thương mại)
- **Công dụng:** Lấy ảnh backdrop, trending movies
- **Lưu ý:** Không cho phép thương mại

---

## Cấu hình file .env

Tạo file `.env` trong thư mục gốc:

```env
# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key

# OMDB API (cho phép thương mại)
OMDB_API_KEY=your_omdb_api_key

# TMDB API (tùy chọn, phi thương mại)
TMDB_API_KEY=your_tmdb_api_key

# Cài đặt kênh
CHANNEL_LANGUAGE=vi
CHANNEL_NAME=PhimHay Review
```

---

## Chạy trên Google Colab

### Bước 1: Upload files lên Google Drive

1. Vào Google Drive: https://drive.google.com
2. Tạo thư mục `Auto_review_youtube`
3. Upload các file sau:
   - `1_colab_api.ipynb` - Notebook chính
   - `.env` - API keys

### Bước 2: Mở notebook trong Colab

1. Vào Google Colab: https://colab.research.google.com
2. Click File → Open notebook → Google Drive
3. Chọn file `1_colab_api.ipynb`

### Bước 3: Chọn GPU runtime

**Chọn GPU trước khi chạy:**
1. Click Runtime → Change runtime type
2. Chọn GPU phù hợp (xem phần bên dưới)
3. Click Save

### Bước 4: Chạy notebook

1. Chạy Cell 1: Mount Google Drive
2. Chạy Cell 2: Install dependencies
3. Chạy Cell 3: Load API keys từ file .env
4. Chạy Cell 4-9: Load các module
5. Chạy Cell 10: Chọn phim và chạy pipeline
6. Chạy Cell 11: Tải video về máy

---

## Chọn GPU tối ưu

### So sánh các loại GPU trên Colab

| GPU | VRAM | Tốc độ | Free/Pro | Ưu điểm | Nhược điểm |
|-----|------|--------|----------|---------|------------|
| **T4** | 16GB | Trung bình | Free | Phổ biến, ổn định | Chậm hơn A100 |
| **V100** | 16GB | Nhanh | Pro | Nhanh hơn T4 | Ít available |
| **A100** | 40GB | Rất nhanh | Pro+ | Nhanh nhất, nhiều VRAM | Đắt, ít available |
| **L4** | 24GB | Nhanh | Pro | Cân bằng tốt | Ít available |
| **CPU** | N/A | Chậm | Free | Không cần GPU | Rất chậm |

### Khuyến nghị cho Movie Review Bot

**Dùng Free Colab (T4):**
- ✅ Đủ cho việc tạo video review phim
- ✅ Thời gian xử lý: 5-10 phút/video
- ✅ Không tốn tiền
- ⚠️ Có thể bị disconnect sau 90 phút không hoạt động

**Dùng Colab Pro (T4/V100):**
- ✅ Ưu tiên GPU tốt hơn
- ✅ Thời gian chạy lâu hơn (24 giờ)
- ✅ Ít bị disconnect hơn

**Dùng Colab Pro+ (A100):**
- ✅ Nhanh nhất
- ✅ Thời gian chạy 24 giờ
- ⚠️ Đắt ($50/tháng)

### Khuyến nghị cụ thể

**Nếu dùng Free Colab:**
- Chọn **T4** (mặc định)
- Đủ cho 1-2 video/ngày
- Không cần GPU mạnh

**Nếu dùng Colab Pro:**
- Chọn **T4** hoặc **V100**
- Tạo được 3-5 video/ngày

**Nếu dùng Colab Pro+:**
- Chọn **A100** nếu cần tạo nhiều video
- Không cần thiết cho việc review phim

---

## Pipeline hoạt động

```
[OMDB API] → Movie Data (title, cast, poster, rating)
     ↓
[DeepSeek AI] → Review Script (15+ min = ~2,500 words)
     ↓
[Edge TTS] → Audio MP3 (neural voice)
     ↓
[Script] → SRT Subtitles (generated from script text)
     ↓
[Pillow + OMDB] → Background Images + Thumbnails
     ↓
[MoviePy + FFmpeg] → Final Video (images + audio + subtitles, 15+ min)
```

---

## Cấu trúc thư mục trên Google Drive

```
MyDrive/Auto_review_youtube/
├── 1_colab_api.ipynb          # Notebook chính
├── .env                        # API keys
└── output/
    ├── videos/                 # Video MP4
    │   ├── 550.mp4            # Fight Club
    │   ├── 680.mp4            # Pulp Fiction
    │   └── ...
    ├── audio/                  # File audio MP3
    │   ├── 550.mp3
    │   └── ...
    ├── subtitles/              # File phụ đề SRT
    │   ├── 550.srt
    │   └── ...
    ├── thumbnails/             # Thumbnail
    │   ├── 550.jpg
    │   └── ...
    └── scripts/                # Script review
        ├── 550_script.txt
        └── ...
```

---

## Hậu kỳ với CapCut

### Bước 1: Import video
1. Mở CapCut
2. Tạo project mới (1920x1080, 30fps)
3. Import video từ Google Drive

### Bước 2: Thêm phụ đề
1. Click **Text** > **Auto Captions**
2. Chọn ngôn ngữ phù hợp
3. CapCut sẽ tự动生成 phụ đề từ audio
4. Hoặc import file .srt đã tải

### Bước 3: Chỉnh sửa
1. Thêm intro/outro
2. Chỉnh màu sắc, hiệu ứng
3. Thêm nhạc nền (royalty-free)
4. Thêm subscribe button

### Bước 4: Export
1. Export ở 1080p, 30fps
2. Upload lên YouTube
3. Thêm title, description, tags

---

## Upload lên YouTube

### Tự động (YouTube API)
- Cần tạo OAuth2 credentials
- Download client_secret.json
- Upload tự động qua API

### Thủ công
1. Vào YouTube Studio
2. Click Upload
3. Chọn video từ Google Drive
4. Thêm title, description, tags
5. Publish

---

## Troubleshooting

### "OMDB_API_KEY not set"
- Kiểm tra file `.env` đã có API key chưa
- Đảm bảo file `.env` nằm trong thư mục `MyDrive/Auto_review_youtube/`

### "DeepSeek API returned 401"
- API key không hợp lệ
- Lấy lại key tại https://platform.deepseek.com

### "Video too short"
- Tăng MIN_WORD_COUNT trong notebook
- Mặc định: 2,500 từ (tiếng Việt), 2,000 từ (tiếng Anh)

### "FFmpeg not found"
- Chạy Cell 2 (Install dependencies) trước
- Đảm bảo đã chọn GPU runtime

### "Movie not found"
- Kiểm tra tên phim chính xác
- Thử tìm kiếm trên OMDB: http://www.omdbapi.com/

---

## Mẹo tối ưu

### Tăng tốc độ
1. Chọn GPU T4 (mặc định)
2. Giảm độ phân giải video (1280x720 thay vì 1920x1080)
3. Giảm FPS (24 thay vì 30)

### Tăng chất lượng
1. Sử dụng voice `vi-VN-HoaiMyNeural` (tiếng Việt)
2. Sử dụng voice `en-US-GuyNeural` (tiếng Anh)
3. Thêm background music (royalty-free)

### Tiết kiệm API
1. Cache kết quả OMDB (không gọi lại cùng 1 phim)
2. Giảm số lượng phim mỗi batch
3. Sử dụng DeepSeek API hiệu quả (giảm max_tokens)

---

## Liên kết hữu ích

- **DeepSeek API:** https://platform.deepseek.com
- **OMDB API:** http://www.omdbapi.com/
- **TMDB API:** https://www.themoviedb.org
- **Google Colab:** https://colab.research.google.com
- **Google Drive:** https://drive.google.com
- **CapCut:** https://www.capcut.com
- **YouTube Studio:** https://studio.youtube.com

---

## Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra Troubleshooting ở trên
2. Đọc error message cẩn thận
3. Đảm bảo API keys đúng
4. Đảm bảo đã chọn GPU runtime

---

## Cập nhật

- **v1.0:** Sử dụng TMDB API (phi thương mại)
- **v1.1:** Chuyển sang OMDB API (cho phép thương mại)
- **v1.2:** Thêm Colab notebook, tự động hóa
