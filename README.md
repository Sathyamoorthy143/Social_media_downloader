# Social Media Downloader

A full-stack application to download high-quality videos and audio from YouTube, Instagram, Facebook, and Pinterest.

## Features

- **Multi-Platform Support**: Download content from YouTube, Instagram, Facebook, and Pinterest.
- **High Quality**: Supports high-resolution video downloads (up to 4K/8K where available) and high-bitrate audio.
- **Format Conversion**: Automatically converts all video downloads to MP4 for maximum compatibility.
- **Proxy Download System**: Ensures reliable file downloads by bypassing client-side redirect issues.
- **Subtitles**: Download subtitles for YouTube videos in various languages.
- **User-Friendly Interface**: Clean and modern React-based frontend with platform-specific themes.
- **Robust Backend**: Python Quart-based backend with efficient handling of large files and concurrent requests.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: Python, Quart, yt-dlp
- **Tools**: `yt-dlp` (YouTube, Facebook, Pinterest), `playwright` (Instagram), `ffmpeg` (Media processing)

## Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **FFmpeg**: Must be installed and added to your system PATH.

## Installation

See [SETUP.md](./SETUP.md) for detailed installation instructions.

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for a comprehensive guide on hosting this application on Vercel (Frontend) and Render/Railway (Backend).

## Usage

1.  **Start the Backend**:
    ```bash
    cd backend
    python main.py
    ```
    The server will start at `http://localhost:5000`.

2.  **Start the Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```
    The application will be accessible at `http://localhost:5173`.

3.  **Download Content**:
    - Paste the URL of the video you want to download.
    - Select the desired format (Video/Audio) and quality.
    - Click "Download".

## API Endpoints

- `GET /search`: Search for videos on YouTube.
- `GET /info`: Get video information.
- `POST /download`: Download video.
- `POST /download_audio`: Download audio.
- `POST /api/instagram`: Download Instagram content.
- `POST /api/facebook`: Download Facebook content.
- `POST /api/pinterest`: Download Pinterest content.
- `GET /proxy_download`: Proxy file download endpoint.

## Developer

Developed by [Sathyamoorthy143](https://github.com/Sathyamoorthy143).

## License

MIT
