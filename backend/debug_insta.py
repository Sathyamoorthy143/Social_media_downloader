from playwright.sync_api import sync_playwright
import time

def debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://thesocialcat.com/tools/instagram-video-downloader")
        
        # Fill input
        page.fill('#instagram-url', 'https://www.instagram.com/p/C-uX1y_S_qA/')
        print("Filled input.")
        
        # Wait a bit for UI update
        time.sleep(1)
        
        # Check button state
        btn = page.query_selector('button[type="submit"]')
        if btn:
            is_disabled = btn.is_disabled()
            print(f"Button disabled state: {is_disabled}")
            if not is_disabled:
                print("Button is enabled!")
        else:
            print("Submit button not found")

        browser.close()

if __name__ == "__main__":
    debug()
