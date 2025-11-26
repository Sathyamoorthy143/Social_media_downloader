from playwright.sync_api import sync_playwright

def debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        print("Navigating to Instagram...")
        page.goto("https://www.instagram.com/p/C-uX1y_S_qA/")
        
        try:
            # Wait for meta tag
            page.wait_for_selector('meta[property="og:image"]', timeout=10000)
            meta = page.query_selector('meta[property="og:image"]')
            if meta:
                content = meta.get_attribute('content')
                print(f"Thumbnail found: {content}")
                
            title_meta = page.query_selector('meta[property="og:title"]')
            if title_meta:
                 print(f"Title found: {title_meta.get_attribute('content')}")
                 
        except Exception as e:
            print(f"Error: {e}")

        browser.close()

if __name__ == "__main__":
    debug()
