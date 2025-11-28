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
        if response.status_code == 200:
            html = response.text
            
            # Helper to extract video from data
            def extract_video_from_data(data):
                try:
                    # Check initialReduxState in props or root
                    if 'initialReduxState' in data:
                         irs = data['initialReduxState']
                    else:
                         irs = data.get('props', {}).get('initialReduxState', {})
                         
                    pins = irs.get('pins', {})
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
                                return video_url, pin_data
                    return None, None
                except:
                    return None, None

            # Try __PWS_INITIAL_PROPS__ first (seems more reliable for some links)
            match_props = re.search(r'<script id="__PWS_INITIAL_PROPS__" type="application/json">(.+?)</script>', html)
            video_url = None
            pin_data = None
            
            if match_props:
                try:
                    data = json.loads(match_props.group(1))
                    video_url, pin_data = extract_video_from_data(data)
                except:
                    pass

            # Try __PWS_DATA__ if not found
            if not video_url:
                match = re.search(r'<script id="__PWS_DATA__" type="application/json">(.+?)</script>', html)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        video_url, pin_data = extract_video_from_data(data)
                    except:
                        pass

            if video_url:
                # Download the video file to TEMP_DIR
                filename = f"{pin_data.get('id', 'pinterest_video')}.mp4"
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
                    "duration": "0:00"
                }

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
