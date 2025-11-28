import requests
import re

def get_meta_content(html, property_name):
    match = re.search(f'<meta property="{property_name}" content="([^"]+)"', html)
    if match:
        return match.group(1)
    return None

def test_fallback(url, name):
    print(f"\n--- Testing {name} Fallback ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html = response.text
            title = get_meta_content(html, "og:title")
            image = get_meta_content(html, "og:image")
            video = get_meta_content(html, "og:video") or get_meta_content(html, "og:video:secure_url")
            
            print(f"Title: {title}")
            print(f"Image: {image}")
            print(f"Video: {video}")
        else:
            print(f"Failed with status {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fallback("https://www.instagram.com/reel/DC5K-C4Sj5u/", "Instagram")
    test_fallback("https://www.pinterest.com/pin/106960559893047239/", "Pinterest")
