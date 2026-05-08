# =============================================
#   GRABZILLA BOT — config.py
#   Developer: @khojiakbar_khaydaraliyev
# =============================================

BOT_TOKEN = "8475743119:AAG7uMJ9XhI2kAGgapPql8sxR9ZK-ht_m5w"
# Admin Telegram ID (o'zingiznikini yozing)
ADMIN_IDS = [6724172090]  # <-- o'zingizning Telegram ID ni qo'ying

# Majburiy obuna kanali (hozircha o'chirilgan)
# Yoqish uchun: REQUIRED_CHANNEL = "@grabzilla_channel" deb o'zgartiring
REQUIRED_CHANNEL = None  # "@grabzilla_channel"

# Bot ma'lumotlari
BOT_USERNAME = "@GrabzillaBot"
BOT_NAME = "Grabzilla"
DEVELOPER = "@khojiakbar_khaydaraliyev"

# YouTube sifat variantlari
YOUTUBE_QUALITIES = {
    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "mp3": "bestaudio/best",
}

# Fayl hajmi chegarasi (MB)
MAX_FILE_SIZE_MB = 50
