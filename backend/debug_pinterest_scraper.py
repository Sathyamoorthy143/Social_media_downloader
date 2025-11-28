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
            
            # Check for __PWS_INITIAL_PROPS__ (seems more promising now)
            match_props = re.search(r'<script id="__PWS_INITIAL_PROPS__" type="application/json">(.+?)</script>', html)
            if match_props:
                 print("Found __PWS_INITIAL_PROPS__ content!")
                 try:
                     props_data = json.loads(match_props.group(1))
                     print("Parsed __PWS_INITIAL_PROPS__")
                     print("Keys:", props_data.keys())
                     
                     # Check for initialReduxState here
                     if 'initialReduxState' in props_data:
                         print("Found initialReduxState in __PWS_INITIAL_PROPS__")
                         irs = props_data['initialReduxState']
                         print("initialReduxState keys:", irs.keys())
                         
                         # Check pins
                         pins = irs.get('pins', {})
                         if pins:
                             print(f"Found {len(pins)} pins in initialReduxState")
                             for pid, pdata in pins.items():
                                 if pdata.get('videos'):
                                     print(f"Pin {pid} has videos!")
                                     print(pdata['videos'])
                                     return
                         else:
                             print("No pins in initialReduxState (inside props)")
                 except Exception as e:
                     print(f"Error parsing __PWS_INITIAL_PROPS__: {e}")

            # Check for __PWS_DATA__ as fallback
            match = re.search(r'<script id="__PWS_DATA__" type="application/json">(.+?)</script>', html)
            if match:
                print("Found __PWS_DATA__ script tag!")
                try:
                    data = json.loads(match.group(1))
                    print(f"Site: {data.get('site')}")
                    print(f"Context: {data.get('context')}")
                except:
                    pass

        else:
            print("Failed to fetch page")
            
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_pinterest_scraper("https://in.pinterest.com/pin/106960559893047239/")
