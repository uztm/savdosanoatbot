from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from database import get_events


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )


def main_menu():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="📅 Tadbirlar ro'yxati")],
            [KeyboardButton(text="📞 Aloqa"), KeyboardButton(text="🌐 Tilni o'zgartirish")]
        ]
    )


def events_keyboard():
    events = get_events()
    if not events:
        return None  # Tadbirlar bo‘lmasa, keyin handlerda "tadbir yo‘q" deb chiqadi

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for e in events:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=e[1], callback_data=f"event_{e[0]}")
        ])
    return kb
