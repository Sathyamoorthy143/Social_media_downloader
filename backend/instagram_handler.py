import logging
import os
from scraper.Youtube import YoutubeVideo
from settings import TEMP_DIR

logger = logging.getLogger(__name__)

def download_instagram(url):
    # Try yt-dlp first (with cookies and mobile UA)
    try:
        # Check for cookies.txt
        cookies_path = os.path.join(os.getcwd(), 'cookies.txt')
        if not os.path.exists(cookies_path):
             cookies_path = None

        yt_video = YoutubeVideo(url, TEMP_DIR, proxies=None, cookies_file=cookies_path, use_browser_cookies=True)
        info = yt_video.dict()
        filename = yt_video.download()
        
        if filename and os.path.exists(filename):
            return {
                "title": info.get('title', 'Instagram Video'),
                "url": url,
                "download_url": f"/api/temp_file/{os.path.basename(filename)}",
                "thumbnail": info.get('thumbnail_url', ''),
                "duration": info.get('length')
            }
    except Exception as e:
        logger.warning(f"yt-dlp failed for Instagram: {e}")
        # Fallback to Instaloader
        pass

    # Fallback: Instaloader
    try:
        import instaloader
        # Use mobile UA
        ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        L = instaloader.Instaloader(user_agent=ua)
        shortcode = url.split("/p/")[1].split("/")[0] if "/p/" in url else url.split("/reel/")[1].split("/")[0]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        video_url = post.video_url
        if video_url:
             # Download manually
             import requests
             filename = f"{shortcode}.mp4"
             file_path = os.path.join(TEMP_DIR, filename)
             
             with requests.get(video_url, stream=True) as r:
                 r.raise_for_status()
                 with open(file_path, 'wb') as f:
                     for chunk in r.iter_content(chunk_size=8192):
                         f.write(chunk)

             return {
                "title": post.caption or "Instagram Video",
                "url": url,
                "download_url": f"/api/temp_file/{filename}",
                "thumbnail": post.url,
                "duration": "0:00"
            }
    except Exception as e:
        logger.error(f"Instaloader failed: {e}")
        return {"error": "Failed to download Instagram video"}

def get_instagram_info(url):
    try:
        import instaloader
        L = instaloader.Instaloader()
        shortcode = url.split("/p/")[1].split("/")[0] if "/p/" in url else url.split("/reel/")[1].split("/")[0]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        return {
            "title": post.caption or "Instagram Video",
            "thumbnail_url": post.url, # This is the image URL
            "length": "0:00", # Instaloader doesn't give duration easily without downloading
            "view_url": url,
            "author": post.owner_username,
            "publish_date": post.date_local.strftime('%Y-%m-%d')
        }
    except Exception as e:
        logger.error(f"Error getting instagram info: {e}")
        return None
