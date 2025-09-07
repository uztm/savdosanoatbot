from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from database import get_events, get_user_language
from translations import get_text
from urllib.parse import urlparse


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )


def main_menu(lang: str = "uz"):
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=get_text("btn_events", lang))],
            [
                KeyboardButton(text=get_text("btn_contact", lang)), 
                KeyboardButton(text=get_text("btn_lang", lang))
            ]
        ]
    )


def events_keyboard():
    events = get_events()
    if not events:
        return None

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for event_id, title in events:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=title, callback_data=f"event_{event_id}")
        ])
    return kb


def event_detail_keyboard(event_id: int, read_more_link: str | None, lang: str = "uz"):
    """Keyboard for event detail with direct link and register button"""
    buttons = []
    
    if read_more_link:  # agar link mavjud bo‘lsa
        buttons.append([
            InlineKeyboardButton(
                text=get_text("btn_read_more", lang),
                url=read_more_link  # callback_data o‘rniga url ishlatyapmiz
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text=get_text("btn_register", lang), 
            callback_data=f"register_{event_id}"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def phone_keyboard(lang: str = "uz"):
    """Keyboard for sending phone number"""
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(
                text=get_text("btn_send_phone", lang), 
                request_contact=True
            )]
        ]
    )


def admin_panel_keyboard(lang: str = "uz"):
    """Admin panel keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_add_event", lang), callback_data="admin_add")],
            [InlineKeyboardButton(text=get_text("btn_manage_events", lang), callback_data="admin_manage")],
            [InlineKeyboardButton(text=get_text("btn_send_message", lang), callback_data="admin_message")]
        ]
    )


def manage_events_keyboard():
    """Keyboard for managing events"""
    events = get_events()
    if not events:
        return None

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for event_id, title in events:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=title, callback_data=f"manage_{event_id}")
        ])
    return kb


def event_management_keyboard(event_id: int, lang: str = "uz"):
    """Keyboard for individual event management"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_archive", lang), callback_data=f"archive_{event_id}")],
            [InlineKeyboardButton(text=get_text("btn_edit", lang), callback_data=f"edit_{event_id}")],
            [InlineKeyboardButton(text=get_text("btn_download", lang), callback_data=f"download_{event_id}")]
        ]
    )