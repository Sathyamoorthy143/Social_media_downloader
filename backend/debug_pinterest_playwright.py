from playwright.sync_api import sync_playwright
import json
import time

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

def run(url):
    with sync_playwright() as p:
        print(f"Launching browser for {url}")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            page.goto(url, timeout=60000)
            print("Page loaded")
            
            # Wait for some content
            page.wait_for_load_state("domcontentloaded")
            print("DOM content loaded")
            time.sleep(5) # Wait a bit for JS to execute
            
            # Take screenshot
            page.screenshot(path="page.png")
            print("Saved screenshot to page.png")

            # Try to get __PWS_INITIAL_PROPS__ from window
            try:
                props_str = page.evaluate("() => JSON.stringify(window.__PWS_INITIAL_PROPS__)")
                print(f"Type of props_str: {type(props_str)}")
                if props_str:
                    print("Found window.__PWS_INITIAL_PROPS__")
                    props = json.loads(props_str)
                    with open("playwright_props.json", "w", encoding="utf-8") as f:
                        json.dump(props, f, indent=2)
                    print("Dumped props to playwright_props.json")
                    
                    url = extract_video_from_data(props)
                    if url:
                        print(f"SUCCESS! Extracted URL from window props: {url}")
                        return
            except Exception as e:
                print(f"Error getting window props: {e}")

            # Try to get __PWS_DATA__ from window
            try:
                data_str = page.evaluate("() => JSON.stringify(window.__PWS_DATA__)")
                print(f"Type of data_str: {type(data_str)}")
                if data_str:
                    print("Found window.__PWS_DATA__")
                    data = json.loads(data_str)
                    url = extract_video_from_data(data)
                    if url:
                        print(f"SUCCESS! Extracted URL from window data: {url}")
                        return
            except Exception as e:
                print(f"Error getting window data: {e}")
                
            # Try to find video tag directly
            try:
                video_src = page.evaluate("() => { const v = document.querySelector('video'); return v ? v.src : null; }")
                if video_src:
                    print(f"SUCCESS! Found video tag src: {video_src}")
                    return
            except Exception as e:
                print(f"Error finding video tag: {e}")

            # Try to find image in JSON-LD
            try:
                image_url = page.evaluate("""() => {
                    const script = document.querySelector('script[type="application/ld+json"]');
                    if (script) {
                        const data = JSON.parse(script.innerText);
                        return data.image || (data.sharedContent && data.sharedContent.image);
                    }
                    return null;
                }""")
                if image_url:
                    print(f"SUCCESS! Found image URL in JSON-LD: {image_url}")
                    return
            except Exception as e:
                print(f"Error finding image in JSON-LD: {e}")

            # Try to find og:image
            try:
                og_image = page.evaluate("() => { const meta = document.querySelector('meta[property=\"og:image\"]'); return meta ? meta.content : null; }")
                if og_image:
                    print(f"SUCCESS! Found og:image: {og_image}")
                    return
            except Exception as e:
                print(f"Error finding og:image: {e}")

            # Dump HTML if all else fails
            with open("playwright_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved playwright_page.html")

        except Exception as e:
            print(f"Playwright error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run("https://in.pinterest.com/pin/106960559893047239/")
