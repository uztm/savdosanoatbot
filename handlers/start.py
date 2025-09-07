from aiogram import Router, types
from aiogram.filters import CommandStart
from database import add_user, set_user_language, get_user_language
from keyboards import language_keyboard, main_menu
from translations import get_text

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    # Save user with name
    add_user(user_id, user_name)
    
    await message.answer(
        get_text("choose_language"),
        reply_markup=language_keyboard()
    )

@router.callback_query(lambda c: c.data.startswith("lang_"))
async def lang_callback(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    
    set_user_language(user_id, lang)

    greeting = get_text("greeting", lang, name=user_name)
    await callback.message.answer(greeting, reply_markup=main_menu(lang))
    await callback.answer(get_text("language_changed", lang))