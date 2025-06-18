"""
Configuration file for TubeFetch Bot
Contains bot token and other settings
"""
import os

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Download Settings
MAX_FILE_SIZE = 80 * 1024 * 1024  # 80MB in bytes
DOWNLOAD_TIMEOUT = 300  # 5 minutes
MAX_FILE_SIZE_4K = 200 * 1024 * 1024  # 200MB for 4K videos
TEMP_DIR = "downloads"

# File Management Settings
AUTO_DELETE_FILES = False  # Set to True to auto-delete files after sending
KEEP_FILES_HOURS = 24  # Hours to keep files before cleanup (if AUTO_DELETE_FILES is False)

# Video Quality Options
VIDEO_QUALITIES = {
    "144p": "worst[height<=144]",
    "240p": "worst[height<=240]",
    "360p": "worst[height<=360]",
    "480p": "worst[height<=480]",
    "720p": "best[height<=720]",
    "1080p": "best[height<=1080]",
    "4K": "best[height<=2160]"
}

# Audio Settings
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = "320"

# Bot Info
BOT_VERSION = "1.0"
CREATOR_NAME = "Mohit Gupta"
CREATOR_USERNAME = "@MohitGu2006"

# Messages
WELCOME_MESSAGE = """👋 *Welcome to TubeFetch Bot*

Your personal assistant to download YouTube videos and songs in various formats.

Select an option below to get started:"""

HELP_MESSAGE = """📌 *How to Use:*

• Click 📥 to download video
• Click 🎵 to download MP3
• Paste any valid YouTube link
• Select quality and wait for download

*Supported Formats:*
📹 Video: 144p, 240p, 360p, 480p, 720p, 1080p, 4K
🎵 Audio: MP3 320kbps

*File Size Limits:*
• Standard quality (up to 1080p): 80MB max
• 4K Ultra HD: 200MB max"""

ABOUT_MESSAGE = f"""ℹ️ *About TubeFetch Bot*

Made with ❤️ by [{CREATOR_NAME}]
Bot Version: {BOT_VERSION}
Contact: {CREATOR_USERNAME}

*Features:*
• High-quality video downloads
• MP3 audio extraction
• Multiple format support
• Fast and reliable service"""
