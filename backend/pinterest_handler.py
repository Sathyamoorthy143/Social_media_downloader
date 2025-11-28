import logging
import os
from yt_dlp import YoutubeDL
from settings import TEMP_DIR

logger = logging.getLogger(__name__)

def download_pinterest(url):
    try:
        # Normalize URL
        if 'pinterest.com' in url:
            url = url.replace('in.pinterest.com', 'www.pinterest.com')
            import re
            url = re.sub(r'https?://[a-z]{2}\.pinterest\.com', 'https://www.pinterest.com', url)

        # Try custom JSON scraping first
        import requests
        import json
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html = response.text
            match = re.search(r'<script id="__PWS_DATA__" type="application/json">(.+?)</script>', html)
            if match:
                data = json.loads(match.group(1))
                # Traverse JSON to find video
                # Path: props -> initialReduxState -> pins -> [id] -> videos -> video_list -> V_720P -> url
                try:
                    pins = data.get('props', {}).get('initialReduxState', {}).get('pins', {})
                    for pin_id, pin_data in pins.items():
                        if pin_data.get('videos'):
                            video_list = pin_data['videos'].get('video_list', {})
                            # Try best quality
                            video_url = None
                            for quality in ['V_720P', 'V_HLSV3_MOBILE', 'V_HLSV4', 'V_EXP7']:
                                if quality in video_list:
                                    video_url = video_list[quality].get('url')
                                    break
                            
                            if not video_url and video_list:
                                # Get first available
                                video_url = list(video_list.values())[0].get('url')

                            if video_url:
                                # Download the video file to TEMP_DIR
                                filename = f"{pin_id}.mp4"
                                file_path = os.path.join(TEMP_DIR, filename)
                                
                                # Stream download
                                with requests.get(video_url, stream=True) as r:
                                    r.raise_for_status()
                                    with open(file_path, 'wb') as f:
                                        for chunk in r.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                            
                                return {
                                    "title": pin_data.get('title') or pin_data.get('grid_title') or "Pinterest Video",
                                    "url": url,
                                    "download_url": f"/api/temp_file/{filename}",
                                    "thumbnail": pin_data.get('images', {}).get('orig', {}).get('url', ''),
                                    "duration": "0:00" # Duration might be in metadata but hard to find
                                }
                except Exception as e:
                    logger.error(f"JSON parsing failed: {e}")
                    # Fallback to yt-dlp if parsing fails
                    pass

        # Fallback to YoutubeVideo class (yt-dlp)
        from scraper.Youtube import YoutubeVideo
        yt_video = YoutubeVideo(url, TEMP_DIR)
        info = yt_video.dict()
        filename = yt_video.download()
        
        if filename and os.path.exists(filename):
            return {
                "title": info.get('title', 'Pinterest Video'),
                "url": url,
                "download_url": f"/api/temp_file/{os.path.basename(filename)}",
                "thumbnail": info.get('thumbnail_url', ''),
                "duration": info.get('length')
            }
        else:
             return {"error": "Download failed or file not found."}

    except Exception as e:
        logger.error(f"Error downloading pinterest: {e}")
        return {"error": str(e)}
