import logging
import sys
import os

# Setup logging to print to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_instagram():
    print("\n--- Testing Instagram ---")
    url = "https://www.instagram.com/reel/DC5K-C4Sj5u/"
    try:
        from instagram_handler import download_instagram
        print(f"Fetching info for {url}...")
        info = download_instagram(url)
        if info and "error" not in info:
            print("Success!")
            print(f"Title: {info.get('title')}")
            print(f"Thumbnail: {info.get('thumbnail')}")
        else:
            print(f"Failed: {info}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

def test_pinterest():
    print("\n--- Testing Pinterest ---")
    url = "https://in.pinterest.com/pin/106960559893047239/"
    try:
        from pinterest_handler import download_pinterest
        print(f"Downloading {url}...")
        result = download_pinterest(url)
        if result and "error" not in result:
             print("Success!")
             print(f"Title: {result.get('title')}")
             print(f"Download URL: {result.get('download_url')}")
        else:
             print(f"Failed: {result}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_instagram()
    test_pinterest()
