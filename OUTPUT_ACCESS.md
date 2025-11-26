# Accessing Downloaded Files

This document explains how to access the files downloaded by the Social Media Downloader.

## Default Download Location

By default, the application saves downloaded files to a temporary directory within the `backend` folder.

-   **Directory**: `backend/temp_files`

## Accessing Files via the Web Interface

When you download a file using the web interface:
1.  The file is processed on the server.
2.  Once processing is complete, a "Download" button or link will appear.
3.  Clicking this link will download the file to your browser's default download location (usually your computer's `Downloads` folder).

## Accessing Files Directly on the Server

If you are running the server locally, you can find the files in:
`e:\PROJECTS\social media downloads\backend\temp_files`

> [!NOTE]
> The application includes a cleanup mechanism that may delete files from the `temp_files` directory after a certain period (default is 30 minutes) to save space.

## Changing the Download Location

Currently, the download location is hardcoded to `temp_files` in `backend/settings.py`.
To change this:
1.  Open `backend/settings.py`.
2.  Modify the `TEMP_DIR` variable:
    ```python
    TEMP_DIR = 'your_custom_folder_name'
    ```
3.  Restart the backend server.
