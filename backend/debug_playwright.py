from playwright.sync_api import sync_playwright

def test_playwright(url, name):
    print(f"\n--- Testing {name} with Playwright ---")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            
            # Wait for some content
            page.wait_for_timeout(5000)
            
            title = page.title()
            print(f"Title: {title}")
            
            # Try to find video tag
            video = page.query_selector("video")
            if video:
                src = video.get_attribute("src")
                print(f"Video src: {src}")
            else:
                print("No video tag found")
                
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_playwright("https://www.instagram.com/reel/DC5K-C4Sj5u/", "Instagram")
    test_playwright("https://www.pinterest.com/pin/106960559893047239/", "Pinterest")
