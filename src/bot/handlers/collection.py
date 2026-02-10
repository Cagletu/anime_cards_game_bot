#pupupu src/bot/handlers/collection.py
#pupupu src/bot/handlers/collection.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.database import get_user_or_create, get_user_collection, update_user_collection_size
from src.core.config import settings

router = Router()

@router.message(Command("collection"))
async def cmd_collection(message: types.Message):
    """Обработчик команды /collection - главное меню"""
    user = await get_user_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Обновляем счетчик карт
    await update_user_collection_size(user.id)
    
    # Клавиатура с вариантами просмотра
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 По редкости", callback_data="collection_by_rarity"),
        InlineKeyboardButton(text="🎌 По аниме", callback_data="collection_by_anime"),
    )
    
    builder.row(
        InlineKeyboardButton(text="⭐ Избранные", callback_data="collection_favorites"),
        InlineKeyboardButton(text="⚔️ В колоде", callback_data="collection_in_deck"),
    )
    
    builder.row(
        InlineKeyboardButton(text="🔝 Самые сильные", callback_data="collection_strongest"),
        InlineKeyboardButton(text="🆕 Последние", callback_data="collection_newest"),
    )
    
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск по имени", callback_data="collection_search"),
        InlineKeyboardButton(text="📈 Статистика", callback_data="collection_stats"),
    )
    
    collection_text = f"""
<b>🃏 КОЛЛЕКЦИЯ КАРТ</b>

Всего карт: <code>{user.collection_size}</code>
Карт в колоде: <code>{len(user.selected_deck) if user.selected_deck else 0}</code>
Избранных: <code>0</code> (скоро)

<b>Выберите способ просмотра:</b>
"""
    
    await message.answer(collection_text, reply_markup=builder.as_markup())

@router.callback_query(lambda c: c.data == "collection_by_rarity")
async def collection_by_rarity(callback: types.CallbackQuery):
    """Показать коллекцию по редкости"""
    user = await get_user_or_create(telegram_id=callback.from_user.id)
    
    # Клавиатура выбора редкости
    builder = InlineKeyboardBuilder()
    
    rarities = ["SSS", "ASS", "S", "A", "B", "C", "D", "E"]
    
    for rarity in rarities:
        builder.add(InlineKeyboardButton(
            text=f"{rarity}",
            callback_data=f"collection_rarity_{rarity}"
        ))
    
    builder.adjust(4, 4)  # 4 кнопки в строке
    
    builder.row(
        InlineKeyboardButton(text="« Назад", callback_data="back_to_collection_menu"),
    )
    
    await callback.message.edit_text(
        "<b>Выберите редкость для просмотра:</b>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("collection_rarity_"))
async def show_rarity_collection(callback: types.CallbackQuery):
    """Показать карты определенной редкости"""
    rarity = callback.data.replace("collection_rarity_", "")
    user = await get_user_or_create(telegram_id=callback.from_user.id)
    
    # Получаем карты этой редкости
    cards = await get_user_collection(user.id, rarity_filter=rarity, page_size=5)
    
    if not cards:
        await callback.message.edit_text(
            f"<b>У вас нет карт редкости {rarity}</b>\n\n"
            f"Попробуйте открыть больше пачек!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="« К выбору редкости", callback_data="collection_by_rarity")]
            ])
        )
        await callback.answer()
        return
    
    # Формируем сообщение
    text = f"<b>📊 Карты редкости {rarity}</b>\n\n"
    
    for i, (user_card, card) in enumerate(cards, 1):
        text += f"{i}. <b>{card.card_name}</b>\n"
        text += f"   Аниме: {card.anime_name}\n"
        text += f"   Уровень: {user_card.level} | 💪{user_card.current_power}\n\n"
    
    text += f"<i>Показано {len(cards)} из {user.collection_size} карт</i>"
    
    # Клавиатура навигации
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"page_{rarity}_prev"),
            InlineKeyboardButton(text="1/1", callback_data="page_info"),
            InlineKeyboardButton(text="➡️", callback_data=f"page_{rarity}_next"),
        ],
        [
            InlineKeyboardButton(text="📊 Другая редкость", callback_data="collection_by_rarity"),
            InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_collection_menu"),
        ]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "collection_stats")
async def collection_stats(callback: types.CallbackQuery):
    """Статистика коллекции"""
    user = await get_user_or_create(telegram_id=callback.from_user.id)
    
    # TODO: Здесь будет логика подсчета карт по редкостям
    # Пока заглушка
    stats_text = f"""
<b>📈 СТАТИСТИКА КОЛЛЕКЦИИ</b>

Всего карт: <code>{user.collection_size}</code>

<b>По редкостям:</b>
SSS: <code>0</code> карт
ASS: <code>0</code> карт
S: <code>0</code> карт
A: <code>0</code> карт
B: <code>0</code> карт
C: <code>0</code> карт
D: <code>0</code> карт
E: <code>{user.collection_size}</code> карт

<b>Самая редкая карта:</b>
Пока нет редких карт

<b>Всего аниме:</b>
<code>0</code> разных аниме

<i>Открывайте пачки чтобы заполнить коллекцию!</i>
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Назад", callback_data="back_to_collection_menu")]
    ])
    
    await callback.message.edit_text(stats_text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_collection_menu")
async def back_to_collection_menu(callback: types.CallbackQuery):
    """Вернуться в меню коллекции"""
    await cmd_collection(callback.message)
    await callback.answer()
