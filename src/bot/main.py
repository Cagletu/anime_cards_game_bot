# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.core.config import settings
from src.database.base import get_db
from src.bot.handlers import register_handlers
from src.bot.middlewares import register_middlewares

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO if not settings.APP_DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    
    # Проверяем обязательные настройки
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен в .env файле!")
        return
    
    # Инициализируем бота с современными настройками
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Инициализируем диспетчер
    dp = Dispatcher()
    
    # Регистрируем middleware (если есть)
    register_middlewares(dp)
    
    # Регистрируем обработчики
    register_handlers(dp)
    
    # Запускаем бота
    logger.info("Запускаем бота...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        # Проверяем подключение к БД перед запуском
        logger.info("Проверяем подключение к БД...")
        
        # Для асинхронной проверки можно использовать async with
        async def test_db():
            async for session in get_db():
                await session.execute("SELECT 1")
                break
        
        asyncio.run(test_db())
        logger.info("Подключение к БД успешно")
        
        # Запускаем бота
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
