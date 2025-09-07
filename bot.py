import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from database import init_db
from handlers import start, events, settings, admin

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize database
    init_db()
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Include routers
    dp.include_router(start.router)
    dp.include_router(events.router)
    dp.include_router(settings.router)
    dp.include_router(admin.router)

    print("🚀 Bot ishga tushdi...")
    print("📊 Database initialized")
    print("🌐 Multi-language support enabled")
    print("✅ All features ready!")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("👋 Bot to'xtatildi")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())