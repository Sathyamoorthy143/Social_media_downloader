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
        try:
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
        except Exception as e:
            logger.warning(f"yt-dlp failed: {e}")

        # Final fallback: Playwright
        logger.info("Attempting Playwright fallback...")
        return download_with_playwright(url)

    except Exception as e:
        logger.error(f"Error downloading pinterest: {e}")
        return {"error": str(e)}

def download_with_playwright(url):
    try:
        from playwright.sync_api import sync_playwright
        import time
        import json

        with sync_playwright() as p:
            # Launch with mobile user agent
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
            )
            page = context.new_page()
            
            try:
                page.goto(url, timeout=60000)
                # Wait for content to load
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=30000)
                    time.sleep(5) # Allow JS to execute
                except:
                    pass

                # 1. Try to find video URL in window props
                video_url = None
                try:
                    props_str = page.evaluate("() => JSON.stringify(window.__PWS_INITIAL_PROPS__)")
                    if props_str:
                        props = json.loads(props_str)
                        # Reuse extraction logic if possible, or simple traversal
                        # For now, let's use a simplified traversal or the helper if we move it out
                        # Since helper is inside download_pinterest, we duplicate logic or move it.
                        # Let's try to find video in the props structure manually for now
                        pass # TODO: Implement deep search if needed, but let's rely on DOM first
                except:
                    pass

                # 2. Try video tag
                if not video_url:
                    try:
                        video_url = page.evaluate("() => { const v = document.querySelector('video'); return v ? v.src : null; }")
                    except:
                        pass

                # 3. Try image if no video
                image_url = None
                if not video_url:
                    # Try JSON-LD first
                    try:
                        image_url = page.evaluate("""() => {
                            const script = document.querySelector('script[type="application/ld+json"]');
                            if (script) {
                                const data = JSON.parse(script.innerText);
                                return data.image || (data.sharedContent && data.sharedContent.image);
                            }
                            return null;
                        }""")
                    except Exception as e:
                        print(f"JSON-LD extraction failed: {e}")

                    # Try og:image if JSON-LD failed
                    if not image_url:
                        try:
                            image_url = page.evaluate("() => { const meta = document.querySelector('meta[property=\"og:image\"]'); return meta ? meta.content : null; }")
                        except Exception as e:
                            print(f"og:image extraction failed: {e}")

                if video_url:
                    # Download video
                    if video_url.startswith('blob:'):
                        # Blob handling is complex, skip for now or try to fetch
                        return {"error": "Blob video URL found, cannot download directly."}
                    
                    filename = f"pinterest_video_{int(time.time())}.mp4"
                    file_path = os.path.join(TEMP_DIR, filename)
                    
                    # Use requests to download
                    import requests
                    with requests.get(video_url, stream=True) as r:
                        r.raise_for_status()
                        with open(file_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                                
                    return {
                        "title": "Pinterest Video (Playwright)",
                        "url": url,
                        "download_url": f"/api/temp_file/{filename}",
                        "thumbnail": "",
                        "duration": "0:00"
                    }

                elif image_url:
                    # Download image
                    filename = f"pinterest_image_{int(time.time())}.jpg"
                    file_path = os.path.join(TEMP_DIR, filename)
                    
                    import requests
                    with requests.get(image_url, stream=True) as r:
                        r.raise_for_status()
                        with open(file_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                                
                    return {
                        "title": "Pinterest Image (Playwright)",
                        "url": url,
                        "download_url": f"/api/temp_file/{filename}",
                        "thumbnail": image_url,
                        "duration": "0:00"
                    }
                else:
                    return {"error": "No video or image found with Playwright."}

            finally:
                browser.close()

    except Exception as e:
        logger.error(f"Playwright fallback failed: {e}")
        return {"error": f"Playwright failed: {str(e)}"}
