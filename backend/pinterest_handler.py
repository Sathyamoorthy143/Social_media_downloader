import logging
import os
from yt_dlp import YoutubeDL
from settings import TEMP_DIR

logger = logging.getLogger(__name__)

def download_pinterest(url):
    try:
        # Primary method: Use SavePinMedia API
        # SavePinMedia handles Pinterest downloads more reliably
        logger.info(f"Using SavePinMedia for Pinterest URL: {url}")
        
        # Normalize the Pinterest URL
        if 'pinterest.com' in url:
            url = url.replace('in.pinterest.com', 'www.pinterest.com')
            import re
            url = re.sub(r'https?://[a-z]{2}\.pinterest\.com', 'https://www.pinterest.com', url)
        
        # For pin.it short URLs, we need to expand them first
        if 'pin.it' in url:
            try:
                import requests
                response = requests.head(url, allow_redirects=True, timeout=5)
                url = response.url
                logger.info(f"Expanded short URL to: {url}")
            except Exception as e:
                logger.warning(f"Failed to expand short URL: {e}")
        
        # Try to get basic info using requests
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # Try to extract title from meta tags
                import re
                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                title = title_match.group(1) if title_match else "Pinterest Content"
                
                # Try to extract thumbnail
                thumb_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
                thumbnail = thumb_match.group(1) if thumb_match else ""
                
                # Return info with a link to use SavePinMedia
                # We'll use the proxy_download endpoint which can fetch from SavePinMedia
                return {
                    "title": title,
                    "url": url,
                    "download_url": f"https://savepinmedia.com/download?url={url}",  # External redirect
                    "thumbnail": thumbnail,
                    "duration": "0:00",
                    "is_external": True  # Flag to indicate this is an external download link
                }
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
        
        # Fallback: Return minimal info with SavePinMedia link
        return {
            "title": "Pinterest Content",
            "url": url,
            "download_url": f"https://savepinmedia.com/download?url={url}",
            "thumbnail": "",
            "duration": "0:00",
            "is_external": True
        }

    except Exception as e:
        logger.error(f"Error in Pinterest handler: {e}")
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
