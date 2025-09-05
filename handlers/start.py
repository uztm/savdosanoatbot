from aiogram import Router, types
from aiogram.filters import CommandStart
from database import add_user, set_user_language
from keyboards import language_keyboard, main_menu

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    add_user(message.from_user.id)
    await message.answer(
        "Tilni tanlang / Choose language / Выберите язык",
        reply_markup=language_keyboard()
    )

@router.callback_query(lambda c: c.data.startswith("lang_"))
async def lang_callback(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    set_user_language(callback.from_user.id, lang)

    full_name = callback.from_user.full_name

    greetings = {
        "uz": (
            f"Assalomu alaykum! {full_name}!\n\n"
            "Savdo-sanoat palatasi Biznes Marafon Botiga xush kelibsiz!\n"
            "Bu yerda siz biznes forumlar, ko‘rgazmalar va yarmarkalar haqida "
            "to‘liq ma’lumot olishingiz va ro‘yxatdan o‘tishingiz mumkin."
        ),
        "ru": (
            f"Ассаламу алейкум! {full_name}!\n\n"
            "Добро пожаловать в Бизнес Марафон Бот Торгово-промышленной палаты!\n"
            "Здесь вы можете получить полную информацию о бизнес-форумах, "
            "выставках и ярмарках, а также зарегистрироваться на них."
        ),
        "en": (
            f"Assalamu alaykum! {full_name}!\n\n"
            "Welcome to the Chamber of Commerce Business Marathon Bot!\n"
            "Here you can get full information about business forums, "
            "exhibitions, and fairs, as well as register for them."
        )
    }

    await callback.message.answer(greetings[lang], reply_markup=main_menu())
    await callback.answer()
