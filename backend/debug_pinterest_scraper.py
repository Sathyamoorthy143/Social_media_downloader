import requests
import json
import re
import logging
import sys

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def test_pinterest_scraper(url):
    print(f"Testing URL: {url}")
    
    # Normalize URL
    if 'pinterest.com' in url:
        url = url.replace('in.pinterest.com', 'www.pinterest.com')
        url = re.sub(r'https?://[a-z]{2}\.pinterest\.com', 'https://www.pinterest.com', url)
    
    print(f"Normalized URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            print(f"HTML length: {len(html)}")
            
            with open("page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved HTML to page.html")
            
            # Helper to extract video from data
            def extract_video_from_data(data):
                try:
                    # Check initialReduxState in props or root
                    if 'initialReduxState' in data:
                         irs = data['initialReduxState']
                    else:
                         irs = data.get('props', {}).get('initialReduxState', {})
                         
                    pins = irs.get('pins', {})
                    if not pins:
                        print("No pins found in initialReduxState")
                        return None
                        
                    for pin_id, pin_data in pins.items():
                        print(f"Checking pin {pin_id}")
                        if pin_data.get('videos'):
                            print("Found 'videos' key in pin data")
                            video_list = pin_data['videos'].get('video_list', {})
                            # Try best quality
                            video_url = None
                            for quality in ['V_720P', 'V_HLSV3_MOBILE', 'V_HLSV4', 'V_EXP7']:
                                if quality in video_list:
                                    video_url = video_list[quality].get('url')
                                    print(f"Found video URL for quality {quality}: {video_url}")
                                    break
                            
                            if not video_url and video_list:
                                # Get first available
                                video_url = list(video_list.values())[0].get('url')
                                print(f"Found fallback video URL: {video_url}")

                            if video_url:
                                return video_url
                    return None
                except Exception as e:
                    print(f"Extraction error: {e}")
                    return None

            # Check for __PWS_INITIAL_PROPS__
            match_props = re.search(r'<script id="__PWS_INITIAL_PROPS__" type="application/json">(.+?)</script>', html)
            if match_props:
                 print("Found __PWS_INITIAL_PROPS__ content!")
                 try:
                     props_data = json.loads(match_props.group(1))
                     print("Parsed __PWS_INITIAL_PROPS__")
                     
                     # Dump full structure to file for analysis
                     with open("structure.txt", "w", encoding="utf-8") as f:
                         json.dump(props_data, f, indent=2)
                     print("Full structure dumped to structure.txt")
                     
                     url = extract_video_from_data(props_data)
                     if url:
                         print(f"SUCCESS! Extracted URL from PROPS: {url}")
                     else:
                         print("FAILED to extract URL from PROPS")
                 except Exception as e:
                     print(f"Error parsing __PWS_INITIAL_PROPS__: {e}")

            # Check for __PWS_DATA__ as fallback
            match = re.search(r'<script id="__PWS_DATA__" type="application/json">(.+?)</script>', html)
            if match:
                print("Found __PWS_DATA__ script tag!")
                try:
                    data = json.loads(match.group(1))
                    print("Parsed __PWS_DATA__")
                    url = extract_video_from_data(data)
                    if url:
                         print(f"SUCCESS! Extracted URL from DATA: {url}")
                    else:
                         print("FAILED to extract URL from DATA")
                except:
                    pass

        else:
            print("Failed to fetch page")
            
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_pinterest_scraper("https://in.pinterest.com/pin/106960559893047239/")
