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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            print(f"HTML length: {len(html)}")
            
            # Check for __PWS_DATA__
            match = re.search(r'<script id="__PWS_DATA__" type="application/json">(.+?)</script>', html)
            if match:
                print("Found __PWS_DATA__ script tag!")
                try:
                    data = json.loads(match.group(1))
                    print("JSON parsed successfully!")
                    
                    # Print keys one by one to avoid truncation
                    print("--- Top Level Keys ---")
                    for k in data.keys():
                        print(f"- {k}")
                    
                    props = data.get('props', {})
                    print("--- Props Keys ---")
                    for k in props.keys():
                        print(f"- {k}")
                        
                    initialReduxState = props.get('initialReduxState', {})
                    print(f"initialReduxState type: {type(initialReduxState)}")
                    if initialReduxState:
                        print("--- initialReduxState Keys ---")
                        for k in initialReduxState.keys():
                            print(f"- {k}")
                    else:
                        print("initialReduxState is empty")

                    # Check for relayResponse
                    if 'relayResponse' in data:
                        print("Found relayResponse!")
                        
                    # Check page title from HTML (simple regex)
                    title_match = re.search(r'<title>(.+?)</title>', html)
                    if title_match:
                        print(f"Page Title: {title_match.group(1)}")
                            
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}")
            else:
                print("No __PWS_DATA__ script tag found in HTML")
                # Print first 500 chars of HTML to see what we got
                print("HTML Start:", html[:500])
        else:
            print("Failed to fetch page")
            
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_pinterest_scraper("https://in.pinterest.com/pin/106960559893047239/")
