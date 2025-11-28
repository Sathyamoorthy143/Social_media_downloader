import logging
import sys
from yt_dlp import YoutubeDL

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def test_url(url, name):
    print(f"\n--- Testing {name} with yt-dlp ---")
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Success! Title: {info.get('title')}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Instagram
    test_url("https://www.instagram.com/reel/DC5K-C4Sj5u/", "Instagram")
    
    # Pinterest (normalized)
    test_url("https://www.pinterest.com/pin/106960559893047239/", "Pinterest")
