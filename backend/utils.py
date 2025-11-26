import json
import random
import requests
import logging
import os
import shutil
import time
from langcodes import find
from quart import url_for
from youtube_urls_validator import validate_url
from urllib.parse import urlparse, parse_qs
from settings import MAX_DOWNLOAD_SIZE, TEMP_DIR, CODECS, AUTH, VISITOR_DATA, PO_TOKEN, PROXIES, DEBUG

logger = logging.getLogger(__name__)

def get_free_mem() -> int:
  disc = shutil.disk_usage('/')
  return disc[2]

def get_first_item(my_list):
    return my_list[0] if my_list else None

def remove_duplicates(items):
  return list(set(items))

def get_proxies():
    reason = "AUTH = False"
    if AUTH:
        reason = "No proxies available"
        if PROXIES:
            logger.info("Using proxies")
            proxies_list = []
            for proxy in PROXIES:
                proxy_dict = {}
                data = proxy.split('@')
                if len(data) == 2:
                    userdata = data[0].split('://')
                    protocol = userdata[0]
                    server = f'{protocol}://{data[1]}'
                    username_password = userdata[1].split(':')
                    username = username_password[0] if len(username_password) > 0 else ''
                    password = username_password[1] if len(username_password) > 1 else ''
                    proxy_dict['server'] = server
                    proxy_dict['username'] = username
                    proxy_dict['password'] = password
                else:
                    proxy_dict['server'] = data[0]  # No authentication case
                proxies_list.append(proxy_dict)
            return proxies_list
    logger.warning("Not using proxies because {}".format(reason))
    return []

def is_valid_youtube_url(url):
    try:
      if validate_url(url=url):
         return True
    except:
      return False

def is_valid_language(value):
    try:
        find(value)
        return True
    except:
      return False

def video_id(value):
    if not value: return
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    # raise ValueError # Don't raise, just return None or handle gracefully
    return None

def get_info(yt):
    try:
        video_info = yt.dict()
        # Safe print for debugging (avoid charmap errors)
        try:
            print(json.dumps(video_info, default=str, ensure_ascii=True))
        except:
            pass
            
        video_info['video_id'] = video_id(video_info.get('view_url'))
        return video_info, None
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return None, str(e)

class YtDlpStream:
    def __init__(self, yt_video, format_str, is_audio=False):
        self.yt_video = yt_video
        self.format_str = format_str
        self.is_audio = is_audio
        self.resolution = "Best"
        self.frame_rate = 30
        self.bit_rate = "128kbps" if is_audio else None
        self.hdr = False
        self.file_name = "video"
        self.adaptive = False # Disable main.py manual merge since yt-dlp handles it

    def download(self):
        return self.yt_video.download_with_format(self.format_str)

def download_content(yt, resolution: str ="", bitrate: str ="", frame_rate: int =30, content_type: str ="video", hdr: bool | None =None):
    try:
        if content_type.lower() == "audio":
            return YtDlpStream(yt, "bestaudio/best", is_audio=True), None
        else:
            # Ignore resolution/framerate for now and just get best
            return YtDlpStream(yt, "bestvideo+bestaudio/best"), None
    except Exception as e:
        logger.error(f"Error downloading {content_type}: {e}")
        return None, f'An error occored: {e}'

def get_captions(yt,lang, translate=False):
    # Captions not fully implemented with yt-dlp wrapper yet in this simplified version
    return None, "Captions not supported in this version"

def delete_file_after_delay(file_path, delay):
    time.sleep(delay)
    if os.path.exists(file_path):
        logger.info("Deleting temp file " + file_path)
        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")

def write_creds_to_file(access_token, refresh_token, expires, visitor_data, po_token, file_path):
    if os.path.exists(file_path): return
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires": int(expires),
        "visitorData": visitor_data,
        "po_token": po_token
    }
    logger.debug(f"creds content: {data}")
    with open(file_path, 'w') as file:
        logger.info("writing creds")
        json.dump(data, file, indent=2)

def fetch_po_token():
  return VISITOR_DATA, PO_TOKEN
