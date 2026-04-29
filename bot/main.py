import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.handlers import start, phone_lookup, credit_score, profile, admin_panel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is empty! Bot cannot start.")
        logger.error("Please set BOT_TOKEN in Railway Variables.")
        return
    
    logger.info(f"BOT_TOKEN loaded: ...{BOT_TOKEN[-10:] if len(BOT_TOKEN) > 10 else 'EMPTY'}")
    logger.info(f"Using DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')[:50]}")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        start.router,
        phone_lookup.router,
        credit_score.router,
        profile.router,
        admin_panel.router,
    )

    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import os
    asyncio.run(main())
