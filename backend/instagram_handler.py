import logging
import asyncio
import os
from scraper.Youtube import YoutubeVideo
from settings import TEMP_DIR

logger = logging.getLogger(__name__)

def download_instagram(url):
    try:
        # Use YoutubeVideo class which wraps yt-dlp
        # We don't need proxies for now as per current setup, or we can pass None
        # The YoutubeVideo class handles the download logic
        
        # Check for cookies.txt
        cookies_path = os.path.join(os.getcwd(), 'cookies.txt')
        if not os.path.exists(cookies_path):
             cookies_path = None
        
        # Create YoutubeVideo instance
        yt_video = YoutubeVideo(url, TEMP_DIR, proxies=None, cookies_file=cookies_path)
        
        # Get info first to get title and thumbnail
        info = yt_video.dict()
        
        # Download the video
        # We use asyncio.run if we are in a sync context, but this function is called via asyncio.to_thread in main.py
        # However, YoutubeVideo.download is synchronous (it uses yt-dlp directly without async)
        # Wait, let's check Youtube.py again. 
        # YoutubeVideo.download is a normal method, not async.
        # So we can call it directly.
        
        filename = yt_video.download()
        
        if filename and os.path.exists(filename):
            # Calculate relative path or just return what main.py expects
            # main.py expects:
            # {
            #     "title": "Instagram Video",
            #     "url": url,
            #     "download_url": f"/temp_file/{os.path.basename(filename)}",
            #     "thumbnail": thumbnail
            # }
            
            return {
                "title": info.get('title') or "Instagram Video",
                "url": url,
                "download_url": f"/api/temp_file/{os.path.basename(filename)}", # main.py route is /api/temp_file/<filename>
                "thumbnail": info.get('thumbnail_url') or ""
            }
        else:
             return {"error": "Download failed or file not found."}

    except Exception as e:
        logger.error(f"Error downloading instagram: {e}")
        return {"error": str(e)}
