import instaloader

def test_instaloader():
    print("Testing Instaloader with custom UA...")
    # Mobile User Agent
    ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    L = instaloader.Instaloader(user_agent=ua)
    
    url = "https://www.instagram.com/reel/DC5K-C4Sj5u/"
    shortcode = "DC5K-C4Sj5u"
    
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"Success! Title: {post.caption}")
        print(f"Thumbnail: {post.url}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_instaloader()
