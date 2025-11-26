import instaloader

def debug():
    L = instaloader.Instaloader()
    url = "https://www.instagram.com/p/C-uX1y_S_qA/"
    shortcode = url.split("/p/")[1].split("/")[0]
    
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"Title: {post.caption}")
        print(f"Video URL: {post.video_url}")
        print(f"Thumbnail: {post.url}") # post.url is the image/thumbnail
        print(f"Is Video: {post.is_video}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug()
