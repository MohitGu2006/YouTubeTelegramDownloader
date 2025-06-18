"""
Utility functions for TubeFetch Bot
Contains helper functions for YouTube downloads and file management
"""
import os
import re
import logging
import asyncio
import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
from config import TEMP_DIR, MAX_FILE_SIZE, MAX_FILE_SIZE_4K, DOWNLOAD_TIMEOUT, VIDEO_QUALITIES, AUTO_DELETE_FILES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ensure_temp_dir():
    """Create temporary download directory if it doesn't exist"""
    Path(TEMP_DIR).mkdir(exist_ok=True)

def cleanup_file(filepath: str, force: bool = False):
    """Remove file if it exists (respects AUTO_DELETE_FILES setting unless forced)"""
    try:
        if os.path.exists(filepath) and (AUTO_DELETE_FILES or force):
            os.remove(filepath)
            logger.info(f"Cleaned up file: {filepath}")
        elif os.path.exists(filepath):
            logger.info(f"File preserved (AUTO_DELETE_FILES=False): {filepath}")
    except Exception as e:
        logger.error(f"Error cleaning up file {filepath}: {e}")

def is_valid_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube link"""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
        r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=[\w-]+'
    ]
    
    return any(re.match(pattern, url) for pattern in youtube_patterns)

def get_video_info(url: str) -> Optional[Dict[str, Any]]:
    """Extract video information from YouTube URL"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'title': info.get('title', 'Unknown Title'),
                'channel': info.get('uploader', 'Unknown Channel'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail'),
                'description': info.get('description', ''),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date'),
            }
    except Exception as e:
        logger.error(f"Error extracting video info: {e}")
        return None

async def download_video(url: str, quality: str, user_id: int) -> Optional[str]:
    """Download video with specified quality"""
    ensure_temp_dir()
    
    output_template = f"{TEMP_DIR}/video_{user_id}_%(title)s.%(ext)s"
    
    ydl_opts = {
        'format': VIDEO_QUALITIES.get(quality, 'best'),
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'extractaudio': False,
        'writeinfojson': False,
        'writedescription': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
    }
    
    try:
        def download_sync():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        # Run download in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await asyncio.wait_for(
            loop.run_in_executor(None, download_sync),
            timeout=DOWNLOAD_TIMEOUT
        )
        
        # Find the downloaded file
        for file in os.listdir(TEMP_DIR):
            if file.startswith(f"video_{user_id}_"):
                filepath = os.path.join(TEMP_DIR, file)
                
                # Check file size (allow larger files for 4K)
                max_size = MAX_FILE_SIZE_4K if quality == "4K" else MAX_FILE_SIZE
                if os.path.getsize(filepath) > max_size:
                    logger.warning(f"File too large: {filepath}")
                    cleanup_file(filepath)
                    return "FILE_TOO_LARGE"
                
                logger.info(f"Video downloaded successfully: {filepath}")
                return filepath
        
        return None
        
    except asyncio.TimeoutError:
        logger.error("Download timeout")
        return "TIMEOUT"
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return None

async def download_audio(url: str, user_id: int) -> Optional[str]:
    """Download audio as MP3"""
    ensure_temp_dir()
    
    output_template = f"{TEMP_DIR}/audio_{user_id}_%(title)s.%(ext)s"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'audioquality': '320K',
        'writeinfojson': False,
        'writedescription': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    
    try:
        def download_sync():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        # Run download in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await asyncio.wait_for(
            loop.run_in_executor(None, download_sync),
            timeout=DOWNLOAD_TIMEOUT
        )
        
        # Find the downloaded file
        for file in os.listdir(TEMP_DIR):
            if file.startswith(f"audio_{user_id}_") and file.endswith('.mp3'):
                filepath = os.path.join(TEMP_DIR, file)
                
                # Check file size
                if os.path.getsize(filepath) > MAX_FILE_SIZE:
                    logger.warning(f"File too large: {filepath}")
                    cleanup_file(filepath)
                    return "FILE_TOO_LARGE"
                
                logger.info(f"Audio downloaded successfully: {filepath}")
                return filepath
        
        return None
        
    except asyncio.TimeoutError:
        logger.error("Download timeout")
        return "TIMEOUT"
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        return None

def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def format_duration(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format"""
    if not seconds:
        return "00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def log_download(user_id: int, username: str, url: str, download_type: str, success: bool):
    """Log download activity for admin review"""
    log_entry = f"User: {user_id} (@{username or 'N/A'}) | Type: {download_type} | URL: {url} | Success: {success}"
    logger.info(f"DOWNLOAD_LOG: {log_entry}")

def cleanup_old_files():
    """Clean up files older than KEEP_FILES_HOURS"""
    from config import KEEP_FILES_HOURS
    import time
    
    if AUTO_DELETE_FILES:
        return  # No cleanup needed if auto-delete is enabled
    
    try:
        current_time = time.time()
        cutoff_time = current_time - (KEEP_FILES_HOURS * 3600)
        
        if not os.path.exists(TEMP_DIR):
            return
            
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(filepath):
                file_age = os.path.getmtime(filepath)
                if file_age < cutoff_time:
                    os.remove(filepath)
                    logger.info(f"Cleaned up old file: {filepath}")
                    
    except Exception as e:
        logger.error(f"Error during scheduled cleanup: {e}")

def get_stored_files_info():
    """Get information about stored files"""
    files_info = []
    total_size = 0
    
    if not os.path.exists(TEMP_DIR):
        return files_info, total_size
        
    try:
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                modified_time = os.path.getmtime(filepath)
                files_info.append({
                    'name': filename,
                    'size': size,
                    'size_formatted': format_file_size(size),
                    'modified': modified_time
                })
                total_size += size
                
    except Exception as e:
        logger.error(f"Error getting files info: {e}")
        
    return files_info, total_size
