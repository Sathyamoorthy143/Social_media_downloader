from playwright.sync_api import sync_playwright

def debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to pinterestdownloader.io...")
        page.goto("https://pinterestdownloader.io/")
        print("Page loaded.")
        
        # List all inputs
        inputs = page.query_selector_all('input')
        print(f"Found {len(inputs)} inputs:")
        for i, inp in enumerate(inputs):
            print(f"Input {i}: {inp.evaluate('el => el.outerHTML')}")
            
        # List all buttons
        buttons = page.query_selector_all('button')
        print(f"Found {len(buttons)} buttons:")
        for i, btn in enumerate(buttons):
            print(f"Button {i}: {btn.evaluate('el => el.outerHTML')}")

        browser.close()

if __name__ == "__main__":
    debug()
