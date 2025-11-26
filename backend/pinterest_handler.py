import logging
import os
from yt_dlp import YoutubeDL
from settings import TEMP_DIR

logger = logging.getLogger(__name__)

def download_pinterest(url):
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best', # Download best quality
            'merge_output_format': 'mp4', # Ensure MP4
        }

        with YoutubeDL(ydl_opts) as ydl:
            # Extract info and download
            info = ydl.extract_info(url, download=True)
            
            # Prepare response
            video_path = ydl.prepare_filename(info)
            # Ensure extension is mp4 if we merged
            if info.get('requested_downloads'):
                 video_path = info['requested_downloads'][0]['filepath']
            
            filename = os.path.basename(video_path)
            
            # Return local path for serving
            return {
                "title": info.get('title', 'Pinterest Video'),
                "url": url,
                "download_url": f"/temp_file/{filename}", # Local server path
                "thumbnail": info.get('thumbnail', ''),
                "duration": info.get('duration')
            }

    except Exception as e:
        logger.error(f"Error downloading pinterest: {e}")
        return {"error": str(e)}
