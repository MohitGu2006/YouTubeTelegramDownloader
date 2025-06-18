"""
TubeFetch Bot - Professional YouTube Downloader Telegram Bot
Main entry point for the bot

Created by: Mohit Gupta (@MohitGu2006)
Version: 1.0
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import start, download, callbacks
from utils import ensure_temp_dir, cleanup_old_files

# Optional: Only needed if you're hosting the bot on Replit or similar
try:
    from keep_alive import keep_alive
    keep_alive()
except ImportError:
    pass  # Ignore if keep_alive.py isn't present

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'),
              logging.StreamHandler()])
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot"""
    # Validate bot token
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "Bot token not provided! Please set BOT_TOKEN environment variable."
        )
        return

    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    dp = Dispatcher()

    # Register routers
    dp.include_router(start.router)
    dp.include_router(download.router)
    dp.include_router(callbacks.router)

    # Ensure temp directory exists
    ensure_temp_dir()

    # Clean up old files on startup
    cleanup_old_files()

    logger.info("🚀 TubeFetch Bot is starting...")

    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
