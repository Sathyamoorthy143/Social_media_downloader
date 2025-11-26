# Deployment Guide

This application consists of two parts: a **React Frontend** and a **Python Backend**. Because the backend requires heavy system dependencies (`ffmpeg`, `playwright` browsers), it cannot be hosted on standard serverless platforms like Vercel's backend functions.

We recommend a **Split Hosting Strategy**:
1.  **Frontend**: Hosted on **Vercel** (Free, fast, global CDN).
2.  **Backend**: Hosted on **Render** or **Railway** (Container-based, supports system binaries).

---

## Part 1: Deploying the Frontend to Vercel

1.  **Push your code to GitHub**: Ensure your project is in a GitHub repository.
2.  **Log in to Vercel**: Go to [vercel.com](https://vercel.com) and sign in with GitHub.
3.  **Add New Project**: Click "Add New..." -> "Project".
4.  **Import Repository**: Select your repository.
5.  **Configure Project**:
    -   **Framework Preset**: Vite
    -   **Root Directory**: Click "Edit" and select the `frontend` folder.
    -   **Build Command**: `npm run build`
    -   **Output Directory**: `dist`
    -   **Environment Variables**:
        -   Add `VITE_API_URL` and set it to your deployed backend URL (e.g., `https://your-backend-app.onrender.com`).
        *Note: You will need to deploy the backend first to get this URL, or update it later.*
6.  **Deploy**: Click "Deploy".

---

## Part 2: Deploying the Backend to Render (Recommended)

Render is great because it supports `Docker` or Python environments where we can install FFmpeg and Playwright.

### Option A: Using Docker (Most Robust)

1.  **Create a `Dockerfile`** in the `backend` folder:
    ```dockerfile
    FROM python:3.9-slim

    # Install system dependencies (FFmpeg, etc.)
    RUN apt-get update && apt-get install -y \
        ffmpeg \
        wget \
        gnupg \
        && rm -rf /var/lib/apt/lists/*

    # Install Playwright dependencies
    RUN pip install playwright
    RUN playwright install-deps
    RUN playwright install chromium

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY . .

    # Expose port
    EXPOSE 5000

    # Run the app
    CMD ["python", "main.py"]
    ```

2.  **Log in to Render**: Go to [render.com](https://render.com).
3.  **New Web Service**: Click "New" -> "Web Service".
4.  **Connect GitHub**: Select your repository.
5.  **Configure**:
    -   **Root Directory**: `backend`
    -   **Runtime**: Docker
    -   **Instance Type**: Free (or Starter for better performance).
6.  **Deploy**: Render will build the Docker image and start the server.

### Option B: Using Python Environment (Simpler but tricky with Playwright)

If you don't use Docker, you need to ensure Render installs FFmpeg and Playwright browsers.
1.  **Build Command**: `pip install -r requirements.txt && playwright install chromium`
2.  **Start Command**: `python main.py`
3.  **Environment Variables**:
    -   `PYTHON_VERSION`: `3.9.0`

---

## Part 3: Connecting Frontend and Backend

1.  **Get Backend URL**: Once Render finishes deploying, copy the service URL (e.g., `https://social-downloader.onrender.com`).
2.  **Update Frontend**:
    -   Go back to your Vercel project settings.
    -   Update the `VITE_API_URL` environment variable with the Render URL.
    -   Redeploy the frontend.
3.  **Update Backend CORS**:
    -   In `backend/settings.py` or `main.py`, ensure CORS is configured to allow requests from your Vercel domain (e.g., `https://your-app.vercel.app`).

## Important Notes

-   **Cold Starts**: On free tiers (Render/Railway), the backend might go to sleep. The first request might take 30-60 seconds to wake it up.
-   **Disk Space**: The backend downloads files to a temporary folder. Ensure your hosting plan has enough ephemeral disk space.
-   **Playwright**: Running headless browsers requires significant RAM. If the free tier crashes, consider upgrading to a basic paid tier ($7/mo on Render).
