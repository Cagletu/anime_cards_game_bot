# src/bot/dispatcher.py
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import (
    start,
    profile,
    collection,
    errors,
)

def get_dispatcher():
    """Создание и настройка диспетчера"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(collection.router)
    dp.include_router(errors.router)
    
    return dp
