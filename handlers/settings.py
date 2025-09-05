from aiogram import Router, types
from keyboards import language_keyboard

router = Router()

@router.message(lambda m: m.text == "📞 Aloqa")
async def contact_handler(message: types.Message):
    await message.answer("Biz bilan bog‘lanish uchun: @your_support")

@router.message(lambda m: m.text == "🌐 Tilni o'zgartirish")
async def change_lang(message: types.Message):
    await message.answer("Tilni tanlang:", reply_markup=language_keyboard())
