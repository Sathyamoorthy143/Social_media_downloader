# Setup Guide

This guide provides step-by-step instructions to set up the Social Media Downloader on Windows.

## Prerequisites

1.  **Python**: Download and install Python 3.8 or higher from [python.org](https://www.python.org/downloads/).
    - **Important**: Check the box "Add Python to PATH" during installation.
2.  **Node.js**: Download and install Node.js (LTS version recommended) from [nodejs.org](https://nodejs.org/).
3.  **FFmpeg**:
    - Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html).
    - Extract the downloaded zip file.
    - Add the `bin` folder (e.g., `C:\ffmpeg\bin`) to your system's PATH environment variable.
    - Verify installation by running `ffmpeg -version` in a terminal.

## Backend Setup

1.  **Navigate to the backend directory**:
    ```powershell
    cd backend
    ```

2.  **Create a virtual environment** (optional but recommended):
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```

4.  **Install Playwright browsers**:
    ```powershell
    playwright install chromium
    ```

5.  **Configure Environment Variables**:
    - The application uses `settings.py` for configuration. You can modify default values there or set environment variables (e.g., `DEBUG`, `AUTH`, `MAX_SIZE`).

6.  **Run the Server**:
    ```powershell
    python main.py
    ```
    The server should now be running at `http://localhost:5000`.

## Frontend Setup

1.  **Navigate to the frontend directory**:
    Open a new terminal window and run:
    ```powershell
    cd frontend
    ```

2.  **Install dependencies**:
    ```powershell
    npm install
    ```

3.  **Run the Development Server**:
    ```powershell
    npm run dev
    ```
    The application should now be accessible at `http://localhost:5173`.

## Troubleshooting

-   **FFmpeg not found**: Ensure the `bin` folder of your FFmpeg installation is correctly added to your system PATH. Restart your terminal after making changes to PATH.
-   **Playwright errors**: Ensure you have run `playwright install chromium`.
-   **Port conflicts**: If ports 5000 or 5173 are in use, you may need to change them in `main.py` or `vite.config.js` respectively.
-   **Activation Error**: If you see `The term '...' is not recognized`, ensure you are including the leading dot and backslash: `.\.venv\Scripts\activate`. Also, ensure you are in the correct directory where `.venv` was created.
-   **SecurityError / UnauthorizedAccess**: If you see "running scripts is disabled on this system", run the following command in PowerShell:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
    Then try activating the virtual environment again.
-   **Playwright not found**: If you see `The term 'playwright' is not recognized`, try running it as a Python module:
    ```powershell
    python -m playwright install chromium
    ```
    If that still fails, ensure you have installed the dependencies: `pip install -r backend/requirements.txt`.
-   **npm error ENOENT (package.json not found)**: This means you are running `npm` commands in the wrong folder. Make sure you have navigated to the `frontend` folder (`cd frontend`) before running `npm install` or `npm run dev`.
