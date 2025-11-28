import asyncio
import logging
from scraper.Youtube import YoutubeVideo

# Configure logging
logging.basicConfig(level=logging.DEBUG)

async def test_url(url, name):
    print(f"\n--- Testing {name} ---")
    try:
        # Create YoutubeVideo instance (simulating what main.py does)
        yt = YoutubeVideo(url, "temp_files")
        
        print(f"Fetching info for {url}...")
        # This calls _fetch_info -> ydl.extract_info
        info = await asyncio.to_thread(yt.dict)
        print("Info fetched successfully!")
        print(f"Title: {info.get('title')}")
        
        print("Attempting download...")
        filename = await asyncio.to_thread(yt.download)
        print(f"Download successful: {filename}")
        
    except Exception as e:
        print(f"ERROR: {e}")

async def main():
    # Instagram Reel
    await test_url("https://www.instagram.com/reel/DC5K-C4Sj5u/", "Instagram")
    
    # Pinterest Pin
    await test_url("https://in.pinterest.com/pin/106960559893047239/", "Pinterest")

if __name__ == "__main__":
    asyncio.run(main())
