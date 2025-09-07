from aiogram import Router, types
from keyboards import language_keyboard, main_menu
from database import get_user_language, set_user_language
from translations import get_text

router = Router()

@router.message(lambda m: m.text and (
    m.text == "📞 Aloqa" or 
    m.text == "📞 Контакты" or 
    m.text == "📞 Contact"
))
async def contact_handler(message: types.Message):
    lang = get_user_language(message.from_user.id)
    await message.answer(get_text("contact_info", lang))

@router.message(lambda m: m.text and (
    m.text == "🌐 Tilni o'zgartirish" or 
    m.text == "🌐 Изменить язык" or 
    m.text == "🌐 Change Language"
))
async def change_lang(message: types.Message):
    await message.answer(get_text("choose_language"), reply_markup=language_keyboard())

@router.callback_query(lambda c: c.data.startswith("lang_"))
async def lang_change_callback(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    set_user_language(user_id, lang)
    
    await callback.message.answer(
        get_text("language_changed", lang), 
        reply_markup=main_menu(lang)
    )
    await callback.answer()