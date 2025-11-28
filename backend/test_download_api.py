import requests
import json

url = "http://localhost:5174/api/download"
payload = {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "link": True
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
