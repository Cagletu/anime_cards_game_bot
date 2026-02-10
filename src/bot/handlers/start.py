from aiogram import Router, types
from aiogram.filters import CommandStart
from src.database.database import get_user_or_create

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = await get_user_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Приветственное сообщение
    welcome_text = f"""
🎮 Добро пожаловать в Anime Cards Game, {message.from_user.first_name}!

📊 Ваш профиль:
👤 Уровень: {user.level}
💰 Монеты: {user.coins}
💎 Кристаллы: {user.crystals}
🃏 Карточек в коллекции: {user.collection_size}

✨ Доступные команды:
/start - Начало
/profile - Профиль
/collection - Коллекция
/open_pack - Открыть пачку карт
/daily - Ежедневная награда
/help - Помощь

🎯 Собери самую сильную колоду и побеждай!
"""
    
    await message.answer(welcome_text)
