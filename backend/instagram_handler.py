import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def download_instagram(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://thesocialcat.com/tools/instagram-video-downloader")
            
            # Wait for input and fill
            page.fill('#instagram-url', url)
            
            # Click download button
            page.click('button[type="submit"]')
            
            # Wait for result
            # Try to find any video or download link
            try:
                # Wait for result container or specific elements
                page.wait_for_selector('video, a[download], .result-container', timeout=15000)
            except:
                pass # Continue to check what we found

            # Extract video src
            video_src = None
            thumbnail = ""
            
            # Check for video tag
            video = page.query_selector('video')
            if video:
                video_src = video.get_attribute('src')
                thumbnail = video.get_attribute('poster') or ""
            
            # Check for download link if video src missing
            if not video_src:
                download_link = page.query_selector('a[download], a[href*="blob:"], a[href*=".mp4"]')
                if download_link:
                    video_src = download_link.get_attribute('href')

            # Check for images if thumbnail missing
            if not thumbnail:
                imgs = page.query_selector_all('img')
                # Simple heuristic: find largest image or one with 'instagram' in src
                for img in imgs:
                    src = img.get_attribute('src')
                    if src and ('instagram' in src or 'fbcdn' in src):
                        thumbnail = src
                        break

            browser.close()
            
            if video_src:
                # Download the file locally to avoid hotlinking/redirect issues
                import requests
                import os
                import uuid
                from settings import TEMP_DIR
                
                try:
                    # Generate unique filename
                    filename = f"instagram_{uuid.uuid4()}.mp4"
                    filepath = os.path.join(TEMP_DIR, filename)
                    
                    # Download with requests
                    # Use a generic user agent to avoid some basic blocks, though the link should be direct
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    
                    with requests.get(video_src, headers=headers, stream=True) as r:
                        r.raise_for_status()
                        with open(filepath, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                                
                    return {
                        "title": "Instagram Video",
                        "url": url,
                        "download_url": f"/temp_file/{filename}",
                        "thumbnail": thumbnail
                    }
                except Exception as e:
                    logger.error(f"Failed to download file from scraped URL: {e}")
                    # Fallback to returning the URL if local download fails (though unlikely to work if local failed)
                    return {
                        "title": "Instagram Video",
                        "url": url,
                        "download_url": video_src,
                        "thumbnail": thumbnail,
                        "warning": "Could not download locally, link might be unstable."
                    }

            else:
                 return {"error": "Could not find download link. The video might be private or the downloader service is busy."}

    except Exception as e:
        logger.error(f"Error scraping instagram: {e}")
        return {"error": str(e)}
