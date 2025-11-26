from playwright.sync_api import sync_playwright
import time

def debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        print("Navigating to publer.io...")
        page.goto("https://publer.io/tools/instagram-downloader")
        
        try:
            # Fill input
            page.fill('input[name="url"]', 'https://www.instagram.com/p/C-uX1y_S_qA/')
            print("Filled input.")
            
            # Click download
            # Need to find the button. Usually near the input.
            # Let's list buttons
            buttons = page.query_selector_all('button')
            submit_btn = None
            for btn in buttons:
                txt = btn.inner_text()
                if 'Download' in txt:
                    submit_btn = btn
                    break
            
            if submit_btn:
                submit_btn.click()
                print("Clicked download.")
            else:
                print("Download button not found by text, trying generic submit")
                page.click('button[type="submit"]')
            
            # Wait for result
            page.wait_for_selector('div[class*="result"], img[src*="instagram"]', timeout=20000)
            print("Result container found.")
            
            # Find image
            img = page.query_selector('img[src*="instagram"], img[src*="fbcdn"]')
            if img:
                print(f"Thumbnail found: {img.get_attribute('src')}")
            else:
                print("Thumbnail NOT found")
                
            # Find download link
            link = page.query_selector('a[href*="download"], a[href*="publer.io"]')
            if link:
                print(f"Download link found: {link.get_attribute('href')}")
                
        except Exception as e:
            print(f"Error: {e}")

        browser.close()

if __name__ == "__main__":
    debug()
