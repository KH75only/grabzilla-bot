# 🦖 Grabzilla Bot

> Instagram, TikTok va YouTube'dan video yuklab oluvchi Telegram bot  
> 👨‍💻 Developer: @khojiakbar_khaydaraliyev

---

## ✅ Funksiyalar

- 📸 Instagram — video va reels yuklab olish
- 🎵 TikTok — video yuklab olish
- ▶️ YouTube — sifat tanlash (360p / 720p / 1080p / MP3)
- 🌐 3 til: O'zbek / Русский / English
- 📢 Majburiy obuna (ixtiyoriy)
- 📊 Admin statistikasi

---

## ⚙️ O'rnatish

### 1. Python o'rnatish
Python 3.10+ kerak: https://python.org

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. FFmpeg o'rnatish (YouTube video birlashtirish uchun)
- **Windows:** https://ffmpeg.org/download.html → PATH ga qo'shing
- **Linux:** `sudo apt install ffmpeg`
- **Mac:** `brew install ffmpeg`

### 4. config.py ni sozlash
```python
BOT_TOKEN = "o'z tokeningiz"
ADMIN_IDS = [sizning_telegram_id]  # https://t.me/userinfobot dan oling

# Majburiy obuna uchun (ixtiyoriy):
REQUIRED_CHANNEL = "@kanal_username"  # yoki None
```

### 5. Botni ishga tushirish
```bash
python bot.py
```

---

## 🚀 Server (Railway / Render) ga deploy qilish

### Railway (bepul):
1. https://railway.app ga o'ting
2. GitHub repo yarating, fayllarni yuklang
3. New Project → Deploy from GitHub
4. Environment variable: `BOT_TOKEN` qo'shing

### Procfile (kerak bo'lsa yarating):
```
worker: python bot.py
```

---

## 📁 Fayl tuzilmasi

```
grabzilla_bot/
├── bot.py           # Asosiy bot
├── config.py        # Token va sozlamalar
├── downloader.py    # Video yuklab olish
├── languages.py     # 3 til tarjimalari
├── database.py      # SQLite baza
├── requirements.txt # Kutubxonalar
└── README.md        # Shu fayl
```

---

## 🔐 Muhim

- Token ni hech kimga bermang
- `grabzilla.db` fayli avtomatik yaratiladi
- `downloads/` papkasi vaqtinchalik fayllar uchun

---

*🦖 Grabzilla Bot — by @khojiakbar_khaydaraliyev*
