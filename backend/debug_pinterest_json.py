import requests
import json
import re

def test_pinterest_json(url):
    print(f"Testing Pinterest JSON for {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html = response.text
            # Look for __PWS_DATA__
            match = re.search(r'<script id="__PWS_DATA__" type="application/json">(.+?)</script>', html)
            if match:
                data = json.loads(match.group(1))
                print("Found JSON data!")
                # Traverse to find video URL
                # This structure varies, but usually in props -> initialReduxState -> pins -> [id] -> videos
                print(str(data)[:500]) # Print start of data to verify
            else:
                print("No JSON data found")
        else:
            print(f"Failed with status {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pinterest_json("https://www.pinterest.com/pin/106960559893047239/")
