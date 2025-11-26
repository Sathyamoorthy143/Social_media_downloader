import logging
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

def download_facebook(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s',
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get('title'),
                "url": info.get('url'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'),
                "download_url": info.get('url')
            }
    except Exception as e:
        logger.error(f"Error downloading facebook: {e}")
        return {"error": str(e)}
