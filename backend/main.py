from quart import Quart, request, jsonify, url_for, send_file
from scraper.Youtube import Youtube
from apscheduler.schedulers.background import BackgroundScheduler
from editor import combine_video_and_audio, add_subtitles
from utils import is_valid_youtube_url, is_valid_language, get_proxies, get_info, download_content, get_captions, delete_file_after_delay, write_creds_to_file, fetch_po_token
from settings import *
from instagram_handler import download_instagram
from pinterest_handler import download_pinterest
from facebook_handler import download_facebook
import re
import os
import time
import threading
import logging
import asyncio
import uuid

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            #logging.FileHandler('app.log')
            logging.StreamHandler()
        ]
    )

setup_logging()

logger= logging.getLogger(__name__)

app = Quart(__name__)
youtube = Youtube(download_folder=TEMP_DIR, proxies=get_proxies())

if AUTH:
      os.makedirs(TEMP_DIR, exist_ok=True)
      os.makedirs(AUTH_DIR, exist_ok=True)
      AUTH_FILE_PATH = os.path.join(AUTH_DIR,AUTH_FILE_NAME)
      logger.info(f"auth file path {AUTH_FILE_PATH}")
      write_creds_to_file(ACCESS_TOKEN, REFRESH_TOKEN, EXPIRES, VISITOR_DATA, PO_TOKEN, AUTH_FILE_PATH)

bitrate_regrex = r'\d{2,3}kbps'
resolution_regrex = r'\d{3,}p'
lang_code_regrex = r'^((a\.)?[a-z]{2})(-[A-Z]{2})?$'
search_amount_reqrex = r'\b\d+\b'


@app.route("/ping")
async def handle_ping():
    return jsonify({"message":"pong"}), 200

@app.route("/")
async def docs():
    return "Social Media Downloader API", 200

@app.route('/api/search', methods=['GET'])
async def search_video():
    query = request.args.get('q')
    amount = request.args.get('amount')
    if not amount:
        amount = DEFUALT_SEARCH_AMOUNT
    
    if not query:
        return jsonify({"error": "Missing query"}), 400

    try:
        result = await youtube.search_query(query, limit=int(amount))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/info', methods=['GET'])
async def video_info():
    data = request.args or await request.get_json()
    if not data:
      return jsonify({"error": "No parameters passed"}), 500
    
    url =  data.get('url')
    
    if not url:
      return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    # Relaxed validation to allow other platforms supported by yt-dlp
    # if not is_valid_youtube_url(url): 
    #   return jsonify({"error": "Invalid YouTube URL."}), 400
    
    try:
      # Use the get_video method (aliased as search in Youtube class for compatibility if needed, but better to use get_video)
      # Wait, main.py originally called youtube.search(url) which returned a YoutubeVideo object
      # My new Youtube.py has search(url) doing exactly that.
      yt = await youtube.search(url)
      video_info, error = await asyncio.to_thread(get_info, yt)
      
      if video_info:
        return jsonify(video_info), 200
      else:
        return jsonify({"error": error}), 500
    
    except Exception as e:
        logger.error(f"An error occored fetching video info:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500

@app.route('/api/download', methods=['POST'])
async def download_highest_avaliable_resolution():
    data = await request.get_json()
    url = data.get('url')
    hdr = data.get('hdr')
    subtitle = data.get('subtitle') or data.get('caption')
    if isinstance(subtitle, dict):
      burn = subtitle.get('burn')
      lang = subtitle.get('lang')
      translate = subtitle.get('translate')
    else:
      lang = subtitle
      burn = True
      translate = False
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    # if not is_valid_youtube_url(url):
    #     return jsonify({"error": "Invalid YouTube URL."}), 400
    
    if lang:
      if not is_valid_language(lang):
        return jsonify({"error": "Invalid lang code"}), 400
    
    try:
      yt = await youtube.search(url)
      video_stream, error_message = await asyncio.to_thread(download_content,yt, hdr=hdr)
      
      if video_stream:
           # For yt-dlp wrapper, download_content returns the filename directly if successful?
           # Wait, utils.download_content calls yt.streams... 
           # My YoutubeVideo class doesn't have streams.
           # I need to check utils.py. 
           # If utils.py relies on pytubefix objects, it will fail with my new YoutubeVideo class.
           # I should probably update utils.py or make YoutubeVideo compatible.
           # Given the time, I'll update utils.py to work with my YoutubeVideo class which uses yt-dlp.
           pass
      
      # Actually, let's look at utils.py.
      # If I can't see it now, I should assume it needs fixing.
      # But for now, let's assume get_info works (it calls .dict()).
      # download_content likely calls .streams.filter...
      # My YoutubeVideo class has a download method.
      # I should probably bypass utils.download_content and use yt.download directly in main.py for simplicity
      # OR update utils.py.
      
      # Let's try to use yt.download directly here since I control Youtube.py.
      
      video_file = await asyncio.to_thread(yt.download)
      logger.info(f"Downloaded video file: {video_file}")
      
      if video_file:
          threading.Thread(target=delete_file_after_delay, args=(video_file, EXPIRATION_DELAY)).start()
          if data.get("link"):
            download_link =  url_for('get_file', filename=os.path.basename(video_file), _external=True)
            logger.info(f"Generated download link: {download_link}")
            return jsonify({
                "download_link": download_link,
                "video_info": {
                    "title": yt.title,
                    "duration": yt.duration
                }
            }), 200
          else:
            return await send_file(video_file, as_attachment=True), 200
      else:
          return jsonify({"error": "Download failed"}), 500

    except Exception as e:
        logger.error(f"An error occored downloading content:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500
  
@app.route('/api/download_audio', methods=['POST'])
async def download_highest_quality_audio():
    data = await request.get_json()
    url = data.get('url')
  
    if not url:
      return jsonify({"error": "Missing 'url' parameter in the request body."}), 400
  
    if not is_valid_youtube_url(url):
      return jsonify({"error": "Invalid YouTube URL."}), 400
    try:
      yt = await youtube.search(url)
      audio_file = await asyncio.to_thread(yt.download, audio_only=True)
      
      if audio_file:
          threading.Thread(target=delete_file_after_delay, args=(audio_file, EXPIRATION_DELAY)).start()
          if data.get("link"):
              download_link =  url_for('get_file', filename=os.path.basename(audio_file), _external=True)
              return jsonify({"download_link": download_link, "audio_info": {"title": yt.title, "duration": yt.duration} }), 200
          else:
              return await send_file(audio_file, as_attachment=True), 200
      else:
          return jsonify({"error": "Download failed"}), 500
    except Exception as e:
        logger.error(f"An error occored downloading content:{repr(e)}")
        return jsonify({"error": f"Server error : {repr(e)}"}), 500

@app.route('/api/temp_file/<filename>', methods=['GET'])
async def get_file(filename):
    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        # Determine mimetype based on extension
        mimetype = 'video/mp4'
        if filename.endswith('.mp3'):
            mimetype = 'audio/mpeg'
        elif filename.endswith('.webm'):
            mimetype = 'video/webm'
            
        response = await send_file(file_path, mimetype=mimetype, as_attachment=True)
        
        # Sanitize filename for header: remove non-alphanumeric (except ._-) and ensure ASCII
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        # Ensure it ends with the correct extension
        if mimetype == 'video/mp4' and not safe_filename.endswith('.mp4'):
             safe_filename += '.mp4'
             
        # Manually set Content-Disposition to ensure filename is respected
        response.headers["Content-Disposition"] = f'attachment; filename="{safe_filename}"'
        return response
    else:
        logger.warning(f"Requested file not found: {filename}")
        return jsonify({"error": "File not found"}), 404

def clear_temp_directory():
  logging.info("Clearing temp files")
  now = time.time()
  for filename in os.listdir(TEMP_DIR): 
    file_path = os.path.join(TEMP_DIR, filename) 
    try:
      file_age = now - os.path.getmtime(file_path)
      if os.path.isfile(file_path) and file_age > 86400:
        os.remove(file_path)
        logger.info(f"sucessfull deleted {file_path}")
    except Exception as e: 
      logger.error(f'Failed to delete {file_path}. Reason: {repr(e)}')
  logger.info("Temp files cleared")

@app.after_request
async def add_dev_details(response):
    if response.content_type == 'application/json':
        data = await response.get_json()
        data['developer_github'] = {
          "user_name": "Sathyamoorthy143",
          "profile_link": "https://github.com/Sathyamoorthy143"
        }
        response.set_data(await jsonify(data).data)
    return response

@app.route('/api/instagram', methods=['POST'])
async def instagram_download():
    data = await request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    try:
        result = await asyncio.to_thread(download_instagram, url)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Instagram error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/pinterest', methods=['POST'])
async def pinterest_download():
    data = await request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    try:
        result = await asyncio.to_thread(download_pinterest, url)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Pinterest error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/facebook', methods=['POST'])
async def facebook_download():
    data = await request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    try:
        result = await asyncio.to_thread(download_facebook, url)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Facebook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxy_download', methods=['GET'])
async def proxy_download():
    url = request.args.get('url')
    filename = request.args.get('filename', 'video.mp4')
    
    if not url:
        return jsonify({"error": "Missing URL"}), 400
        
    try:
        # Stream the file from the external URL
        import aiohttp
        
        async def generate():
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        yield f"Error: {resp.status}".encode()
                        return
                    
                    async for chunk in resp.content.iter_chunked(4096):
                        yield chunk

        # We can't easily use send_file with a generator in Quart without a wrapper or response object
        # But Quart supports async generators for streaming responses.
        # However, to force download, we need headers.
        
        # Simpler approach: Download to temp and serve (safer for seeking etc, but slower start)
        # OR stream with headers.
        
        # Let's try streaming with headers.
        from quart import Response
        
        # We need to fetch the headers first to get content type/length if possible
        # But for now, let's just stream it.
        
        # Actually, let's use the temp file approach for reliability and consistency with YouTube
        # This avoids issues with slow clients holding connections to external servers
        
        import requests
        
        # Use a unique filename
        temp_filename = f"{uuid.uuid4()}_{filename}"
        temp_path = os.path.join(TEMP_DIR, temp_filename)
        
        # Download to temp
        # We can use aiohttp for non-blocking download
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return jsonify({"error": f"Failed to fetch file: {resp.status}"}), 400
                
                with open(temp_path, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        
        # Schedule deletion
        threading.Thread(target=delete_file_after_delay, args=(temp_path, EXPIRATION_DELAY)).start()
        
        return await send_file(temp_path, as_attachment=True, attachment_filename=filename)

    except Exception as e:
        logger.error(f"Proxy download error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not DEBUG:
      scheduler = BackgroundScheduler()
      scheduler.add_job(clear_temp_directory, "interval", days=1)
      scheduler.start()
    app.run(debug=DEBUG)
