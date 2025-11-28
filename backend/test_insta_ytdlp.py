import asyncio
import os
import sys
from yt_dlp import YoutubeDL

def test():
    url = "https://www.instagram.com/p/C-uX1y_S_qA/"
    print(f"Testing URL: {url}")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiesfrombrowser': ('chrome',), 
    }
    
    with open("test_result_cookies.txt", "w") as f:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                f.write("Extracting info with cookies from chrome...\n")
                info = ydl.extract_info(url, download=False)
                f.write(f"Title: {info.get('title')}\n")
                f.write("Success!\n")
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    test()
