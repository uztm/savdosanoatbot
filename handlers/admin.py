from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from database import add_event

router = Router()


# --- STATE MACHINE ---
class AddEventStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_image = State()
    waiting_for_description = State()


# --- ADMIN PANEL ---
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("❌ Siz admin emassiz.")
    
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Tadbir qo‘shish", callback_data="admin_add")],
            [InlineKeyboardButton(text="📦 Tadbirlarni arxivlash", callback_data="admin_archive")],
        ]
    )
    await message.answer("🔐 Admin panelga xush kelibsiz:", reply_markup=kb)


# --- ADD EVENT START ---
@router.callback_query(F.data == "admin_add")
async def admin_add_event(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Siz admin emassiz", show_alert=True)

    await callback.message.answer("✍️ Avval tadbir nomini (title) yuboring:")
    await state.set_state(AddEventStates.waiting_for_title)
    await callback.answer()


# --- GET TITLE ---
@router.message(AddEventStates.waiting_for_title, F.text)
async def get_event_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    await message.answer("📸 Endi tadbir rasmini yuboring:")
    await state.set_state(AddEventStates.waiting_for_image)


# --- GET IMAGE ---
@router.message(AddEventStates.waiting_for_image, F.photo)
async def get_event_image(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(image=photo_id)
    await message.answer("📝 Endi tadbir tavsifini yuboring:")
    await state.set_state(AddEventStates.waiting_for_description)


# --- GET DESCRIPTION ---
@router.message(AddEventStates.waiting_for_description, F.text)
async def get_event_description(message: types.Message, state: FSMContext):
    description = message.text.strip()
    data = await state.get_data()

    title = data.get("title")
    image = data.get("image")

    # SQLite ga yozamiz
    add_event(title=title, description=description, image_url=image)

    await message.answer("✅ Tadbir muvaffaqiyatli qo‘shildi.")
    await state.clear()
