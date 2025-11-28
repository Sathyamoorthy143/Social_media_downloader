# Social Media Downloader

A full-stack application to download high-quality videos and audio from YouTube, Instagram, Facebook, and Pinterest.

![Social Media Downloader](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![Node](https://img.shields.io/badge/Node-16+-green.svg)

## ✨ Features

- **Multi-Platform Support**: Download content from YouTube, Instagram, Facebook, and Pinterest
- **High Quality**: Supports high-resolution video downloads (up to 4K/8K where available)
- **Smart Pinterest Integration**: Uses SavePinMedia for reliable Pinterest downloads
- **Format Conversion**: Automatically converts all video downloads to MP4
- **Link Preview**: See video thumbnails and metadata before downloading
- **User-Friendly Interface**: Modern React-based UI with platform-specific themes
- **Robust Backend**: Python Quart-based API with efficient file handling

## 🛠️ Tech Stack

- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: Python, Quart, yt-dlp
- **Tools**: `yt-dlp`, `playwright`, `instaloader`, `ffmpeg`

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **FFmpeg**: Must be installed and added to your system PATH
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

---

## 🚀 Local Development Setup

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (for Instagram):
   ```bash
   playwright install chromium
   ```

5. **Create a `.env` file** (optional) in the `backend` directory:
   ```env
   DEBUG=True
   TEMP_DIR=temp_files
   EXPIRATION=1800
   MAX_SIZE=2147483648
   ```

6. **Run the backend**:
   ```bash
   python main.py
   ```
   Server will start at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create a `.env` file** in the `frontend` directory:
   ```env
   VITE_API_URL=http://localhost:5000
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```
   Application will be accessible at `http://localhost:5173`

---

## 🌐 Vercel Deployment

### Backend Deployment (Recommended: Railway/Render)

**Important**: Vercel has serverless function limitations (50MB size limit, 10s execution timeout) which make it unsuitable for the backend. Deploy the backend to **Railway**, **Render**, or **Heroku** instead.

#### Option 1: Railway (Recommended)

1. **Create `railway.json`** in the `backend` directory:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "python main.py",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

2. **Push to GitHub** and connect to Railway:
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Set the root directory to `backend`

3. **Configure environment variables** in Railway:
   ```env
   DEBUG=False
   PORT=5000
   ```

4. **Deploy**: Railway will automatically build and deploy
5. **Get the public URL**: Copy your Railway app URL (e.g., `https://your-app.railway.app`)

#### Option 2: Render

1. **Create `render.yaml`** in the project root:
   ```yaml
   services:
     - type: web
       name: social-downloader-api
       env: python
       buildCommand: "cd backend && pip install -r requirements.txt && playwright install chromium"
       startCommand: "cd backend && python main.py"
       envVars:
         - key: DEBUG
           value: False
   ```

2. **Push to GitHub** and deploy on Render:
   - Go to [render.com](https://render.com)
   - New → Web Service → Connect your repo
   - Follow the prompts

### Frontend Deployment (Vercel)

1. **Update `vite.config.js`** to include base URL if deploying to a subdirectory:
   ```javascript
   import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'

   export default defineConfig({
     plugins: [react()],
     server: {
       proxy: {
         '/api': 'http://localhost:5000'
       }
     }
   })
   ```

2. **Create `vercel.json`** in the `frontend` directory:
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "framework": "vite",
     "rewrites": [
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```

3. **Set environment variable** in Vercel:
   - Go to your Vercel project → Settings → Environment Variables
   - Add:
     ```
     VITE_API_URL=https://your-backend-url.railway.app
     ```
   - Replace with your actual backend URL from Railway/Render

4. **Deploy to Vercel**:
   
   **Option A: CLI**
   ```bash
   cd frontend
   npm install -g vercel
   vercel --prod
   ```

   **Option B: GitHub Integration**
   - Push your code to GitHub
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Add the environment variable `VITE_API_URL`
   - Deploy

5. **Configure CORS** in backend `main.py`:
   ```python
   from quart_cors import cors

   app = Quart(__name__)
   app = cors(app, allow_origin="https://your-vercel-app.vercel.app")
   ```

---

## 📦 Environment Variables

### Backend `.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `True` | Enable debug mode for development |
| `TEMP_DIR` | `temp_files` | Directory for temporary file storage |
| `EXPIRATION` | `1800` | File expiration time in seconds (30 min) |
| `MAX_SIZE` | `2147483648` | Max download size in bytes (2GB) |
| `PORT` | `5000` | Server port (for production) |

### Frontend `.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:5000` | Backend API URL |

---

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q=query` | Search YouTube videos |
| GET | `/api/info?url=VIDEO_URL` | Get video metadata |
| POST | `/api/download` | Download video (YouTube) |
| POST | `/api/download_audio` | Download audio (YouTube) |
| POST | `/api/instagram` | Download Instagram content |
| POST | `/api/pinterest` | Get Pinterest download info |
| POST | `/api/facebook` | Download Facebook content |
| GET | `/api/temp_file/:filename` | Retrieve downloaded file |
| GET | `/api/proxy_download` | Proxy external file download |

---

## 🔧 Troubleshooting

### Common Issues

1. **"Failed to fetch video info"**
   - Ensure backend is running on the correct port
   - Check CORS settings if frontend and backend are on different domains
   - Verify `VITE_API_URL` matches your backend URL

2. **Pinterest downloads failing**
   - The app now redirects to SavePinMedia for reliable Pinterest downloads
   - If SavePinMedia link doesn't work, check if the Pinterest URL is public

3. **Instagram downloads not working**
   - Ensure Playwright is installed: `playwright install chromium`
   - Try using `instaloader` fallback (automatic)

4. **Videos downloading in wrong format**
   - Ensure FFmpeg is installed and in your PATH
   - Check backend logs for format conversion errors

5. **Connection refused error**
   - Backend not running - start it with `python main.py`
   - Port conflict - change port in backend `.env` or `main.py`

---

## 👨‍💻 Developer

Developed by [Sathyamoorthy143](https://github.com/Sathyamoorthy143)

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Universal video downloader
- [SavePinMedia](https://savepinmedia.com) - Pinterest download service
- [Playwright](https://playwright.dev) - Browser automation
- [Instaloader](https://instaloader.github.io) - Instagram downloader
