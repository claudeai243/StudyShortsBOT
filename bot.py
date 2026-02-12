import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import config
from database import db
from handlers import user_router, admin_router
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    
    await db.connect()
    logger.info("Database connected")
    try:
        await bot.send_message(
            config.ADMIN_ID,
            "🟢 <b>Бот запущен!</b>\n\n"
            "Используйте /admin для доступа к панели управления.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Failed to send startup message to admin: {e}")


async def on_shutdown(bot: Bot):
    
    await db.disconnect()
    logger.info("Database disconnected")
    try:
        await bot.send_message(
            config.ADMIN_ID,
            "🔴 <b>Бот остановлен!</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass


async def main():
    
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    logger.info("Starting bot...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
