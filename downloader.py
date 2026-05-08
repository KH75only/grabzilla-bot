# =============================================
#   GRABZILLA BOT — downloader.py
#   Developer: @khojiakbar_khaydaraliyev
# =============================================

import os
import uuid
import yt_dlp

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def detect_platform(url: str) -> str:
    u = url.lower()
    if "instagram.com" in u:
        return "instagram"
    elif "tiktok.com" in u or "vm.tiktok.com" in u or "vt.tiktok.com" in u:
        return "tiktok"
    elif "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    elif "twitter.com" in u or "x.com" in u:
        return "twitter"
    elif "facebook.com" in u or "fb.watch" in u:
        return "facebook"
    else:
        return "unknown"


def _base_opts(file_id: str) -> dict:
    return {
        "outtmpl": os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "merge_output_format": "mp4",
    }


def _find_file(file_id: str) -> str | None:
    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(file_id):
            return os.path.join(DOWNLOAD_DIR, f)
    return None


def download_video(url: str, quality: str = None) -> dict:
    platform = detect_platform(url)
    if platform == "unknown":
        return {"success": False, "error": "unsupported"}

    file_id = str(uuid.uuid4())[:8]
    opts = _base_opts(file_id)

    if platform == "youtube":
        if quality == "mp3":
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        elif quality == "240p":
            opts["format"] = "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[height<=240]"
        elif quality == "360p":
            opts["format"] = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]"
        elif quality == "480p":
            opts["format"] = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]"
        elif quality == "720p":
            opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"
        elif quality == "1080p":
            opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"
        else:
            opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"

    elif platform == "instagram":
        opts["format"] = "best"
        opts["http_headers"] = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }

    elif platform == "tiktok":
        opts["format"] = "best"
        opts["http_headers"] = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975U) AppleWebKit/537.36"
        }

    else:
        opts["format"] = "best"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)

        file_path = _find_file(file_id)
        if not file_path:
            return {"success": False, "error": "file_not_found"}

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


def get_video_info(url: str) -> dict:
    """YouTube video ma'lumotlari va har bir sifat hajmini olish"""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "nocheckcertificate": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = {}
        seen = {}
        for f in info.get("formats", []):
            h = f.get("height") or 0
            size = f.get("filesize") or f.get("filesize_approx") or 0
            size_mb = round(size / 1024 / 1024, 1) if size else 0

            for limit, key in [(240, "240p"), (360, "360p"), (480, "480p"), (720, "720p"), (1080, "1080p")]:
                if h <= limit and size_mb:
                    if key not in seen or seen[key] < size_mb:
                        seen[key] = size_mb
                    break

        for k, v in seen.items():
            formats[k] = v

        return {
            "title": info.get("title", "YouTube video"),
            "formats": formats,
        }
    except Exception:
        return {"title": "YouTube video", "formats": {}}


def cleanup_file(file_path: str):
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
