#!/usr/bin/env python3
"""
Точка входа для запуска приложения
"""
import uvicorn
import asyncio
import sys
from src.core.config import settings

def run_api():
    """Запуск FastAPI сервера"""
    uvicorn.run(
        "src.api.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level="info"
    )

def run_bot():
    """Запуск Telegram бота"""
    from src.bot.main import main as bot_main
    asyncio.run(bot_main())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "api":
            run_api()
        elif command == "bot":
            run_bot()
        elif command == "both":
            # Запуск и API и бота (для разработки)
            import threading
            api_thread = threading.Thread(target=run_api)
            api_thread.start()
            run_bot()
        else:
            print("Usage: python run.py [api|bot|both]")
    else:
        print("Usage: python run.py [api|bot|both]")