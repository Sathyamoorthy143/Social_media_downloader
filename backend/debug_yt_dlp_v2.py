import logging
import sys
from yt_dlp import YoutubeDL

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def test_url(url, name):
    print(f"\n--- Testing {name} with yt-dlp ---")
    ydl_opts = {
        'quiet': True, # Reduce noise
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        }
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"SUCCESS: Found title: {info.get('title')}")
            print(f"Thumbnail: {info.get('thumbnail')}")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    # Instagram
    test_url("https://www.instagram.com/reel/DC5K-C4Sj5u/", "Instagram")
    
    # Pinterest (normalized)
    test_url("https://www.pinterest.com/pin/106960559893047239/", "Pinterest")
