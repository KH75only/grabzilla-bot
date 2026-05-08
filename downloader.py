# =============================================
#   GRABZILLA BOT — downloader.py
#   Developer: @khojiakbar_khaydaraliyev
# =============================================

import os
import re
import uuid
import yt_dlp


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def detect_platform(url: str) -> str:
    """Platformani aniqlash"""
    url = url.lower()
    if "instagram.com" in url:
        return "instagram"
    elif "tiktok.com" in url or "vm.tiktok.com" in url:
        return "tiktok"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    elif "facebook.com" in url or "fb.watch" in url:
        return "facebook"
    else:
        return "unknown"


def download_video(url: str, quality: str = None) -> dict:
    """
    Videoni yuklab olish.
    Qaytaradi: {"success": True, "file": "path/to/file", "platform": "..."}
    yoki: {"success": False, "error": "xato matni"}
    """
    platform = detect_platform(url)

    if platform == "unknown":
        return {"success": False, "error": "unsupported"}

    file_id = str(uuid.uuid4())[:8]
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    # yt-dlp sozlamalari
    ydl_opts = {
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }

    # YouTube sifat tanlash
    if platform == "youtube":
        if quality == "mp3":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        elif quality == "360p":
            ydl_opts["format"] = "bestvideo[height<=360]+bestaudio/best[height<=360]/best[height<=360]"
        elif quality == "720p":
            ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]/best[height<=720]"
        elif quality == "1080p":
            ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best[height<=1080]"
        else:
            ydl_opts["format"] = "best[height<=720]"

    # Instagram / TikTok / boshqalar
    else:
        ydl_opts["format"] = "best"
        # Instagram uchun cookies (agar kerak bo'lsa)
        # ydl_opts["cookiefile"] = "cookies.txt"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Yuklab olingan faylni topish
            if quality == "mp3":
                ext = "mp3"
            else:
                ext = info.get("ext", "mp4")

            file_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.{ext}")

            # Fayl mavjudligini tekshirish
            if not os.path.exists(file_path):
                # Boshqa kengaytmani qidirish
                for f in os.listdir(DOWNLOAD_DIR):
                    if f.startswith(file_id):
                        file_path = os.path.join(DOWNLOAD_DIR, f)
                        break

            if not os.path.exists(file_path):
                return {"success": False, "error": "file_not_found"}

            # Hajmini tekshirish (50MB)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb > 50:
                os.remove(file_path)
                return {"success": False, "error": "too_large"}

            return {
                "success": True,
                "file": file_path,
                "platform": platform,
                "size_mb": round(size_mb, 2),
                "is_audio": quality == "mp3",
            }

    except yt_dlp.utils.DownloadError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def cleanup_file(file_path: str):
    """Faylni o'chirish"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
