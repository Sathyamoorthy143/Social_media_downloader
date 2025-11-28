import logging
import asyncio
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

class Youtube:
    def __init__(self, download_folder, proxies=None):
        self.download_folder = download_folder
        self.proxies = proxies

    async def get_video(self, url):
        return YoutubeVideo(url, self.download_folder, self.proxies)

    # Alias for backward compatibility if main.py calls it 'search' for URL lookup
    async def search(self, url, only_video=False, only_caption=False):
        return YoutubeVideo(url, self.download_folder, self.proxies)

    async def search_query(self, query, limit=20):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': f'ytsearch{limit}',
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, query, download=False)
                if 'entries' in info:
                    return {'result': [self._format_search_result(entry) for entry in info['entries']]}
                return {'result': []}
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {'result': []}

    def _format_search_result(self, entry):
        return {
            'id': entry.get('id'),
            'title': entry.get('title'),
            'thumbnails': [{'url': entry.get('thumbnail')}] if entry.get('thumbnail') else [],
            'duration': entry.get('duration_string'),
            'link': entry.get('url'),
            # Add other fields as expected by frontend if needed
        }

class YoutubeVideo:
    def __init__(self, url, download_folder, proxies=None, cookies_file=None):
        self.url = url
        self.download_folder = download_folder
        self.proxies = proxies
        self._info = None
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
        }
        if cookies_file and os.path.exists(cookies_file):
            self.ydl_opts['cookiefile'] = cookies_file
        # Add proxy if needed
        # if proxies: self.ydl_opts['proxy'] = proxies

    @property
    def title(self):
        if not self._info: self._fetch_info()
        return self._info.get('title')

    @property
    def duration(self):
        if not self._info: self._fetch_info()
        return self._info.get('duration')

    def dict(self):
        if not self._info: self._fetch_info()
        # Map yt-dlp info to expected format
        return {
            'title': self._info.get('title'),
            'thumbnail_url': self._info.get('thumbnail'),
            'length': self._info.get('duration_string') or str(self._info.get('duration')),
            'view_url': self._info.get('webpage_url'),
            'author': self._info.get('uploader'),
            'publish_date': self._info.get('upload_date'),
            # Add other fields as needed
        }

    def _fetch_info(self):
        with YoutubeDL(self.ydl_opts) as ydl:
            self._info = ydl.extract_info(self.url, download=False)

    def download(self, audio_only=False):
        opts = self.ydl_opts.copy()
        if audio_only:
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # Force MP4 format
            opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            opts['merge_output_format'] = 'mp4'
        
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            return ydl.prepare_filename(info)

    def download_with_format(self, format_str):
        opts = self.ydl_opts.copy()
        opts['format'] = format_str
        # If audio format, ensure postprocessing if needed, but for now trust the format string
        if 'audio' in format_str:
             opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            return ydl.prepare_filename(info)
