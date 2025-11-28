from scraper.Youtube import YoutubeVideo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

url = "https://pin.it/75RCTYuFu"
print(f"Testing download for: {url}")

try:
    yt_video = YoutubeVideo(url, "temp_files")
    # We need to simulate what pinterest_handler does:
    # It calls yt_video.dict() then yt_video.download()
    
    print("Fetching info...")
    info = yt_video.dict()
    print(f"Title: {info.get('title')}")
    
    print("Attempting download...")
    filename = yt_video.download()
    print(f"Download successful: {filename}")

except Exception as e:
    print(f"Caught exception: {e}")
