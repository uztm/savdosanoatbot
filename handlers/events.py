from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import events_keyboard, event_detail_keyboard, phone_keyboard, main_menu
from database import (
    get_event_detail, get_user_language, add_registration, 
    is_user_registered
)
from translations import get_text
from urllib.parse import urlparse
import webbrowser

router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()


@router.message(lambda m: m.text and (
    m.text == "📅 Tadbirlar ro'yxati" or 
    m.text == "📅 Список мероприятий" or 
    m.text == "📅 Events List"
))
async def show_events(message: types.Message):
    lang = get_user_language(message.from_user.id)
    kb = events_keyboard()
    
    if kb and kb.inline_keyboard:
        await message.answer(get_text("events_list", lang), reply_markup=kb)
    else:
        await message.answer(get_text("no_events", lang))


@router.callback_query(lambda c: c.data.startswith("event_"))
async def event_detail(callback: types.CallbackQuery):
    try:
        event_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        return await callback.answer("❌ Invalid event ID", show_alert=True)

    lang = get_user_language(callback.from_user.id)
    event = get_event_detail(event_id)

    if not event:
        await callback.message.answer(get_text("event_not_found", lang))
        return await callback.answer()

    title, desc, image_url, read_more_link = event
    caption = f"<b>{title}</b>\n\n{desc}"
    
    # Create keyboard with direct link + register button
    kb = event_detail_keyboard(event_id, read_more_link, lang)

    if image_url:
        try:
            await callback.message.answer_photo(
                photo=image_url,
                caption=caption,
                reply_markup=kb,
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.answer(caption, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.answer(caption, reply_markup=kb, parse_mode="HTML")

    await callback.answer()


# Remove the separate read_more_handler since we now use direct URL buttons
# @router.callback_query(lambda c: c.data.startswith("read_more_"))
# This handler is no longer needed as we use direct URL buttons in the keyboard


@router.callback_query(lambda c: c.data.startswith("register_"))
async def register_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        event_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        return await callback.answer("❌ Invalid event ID", show_alert=True)

    user_id = callback.from_user.id
    lang = get_user_language(user_id)

    # Check if already registered
    if is_user_registered(user_id, event_id):
        await callback.answer(get_text("already_registered", lang), show_alert=True)
        return

    # Start registration process
    await state.update_data(event_id=event_id)
    await callback.message.answer(get_text("enter_name", lang))
    await state.set_state(RegistrationStates.waiting_for_name)
    await callback.answer()


@router.message(RegistrationStates.waiting_for_name, F.text)
async def get_registration_name(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    name = message.text.strip()
    
    if not name:
        await message.answer(get_text("enter_name", lang))
        return
    
    await state.update_data(user_name=name)
    await message.answer(
        get_text("send_phone", lang),
        reply_markup=phone_keyboard(lang)
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def get_registration_phone(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    phone_number = message.contact.phone_number
    
    data = await state.get_data()
    event_id = data.get("event_id")
    user_name = data.get("user_name")
    
    # Save registration
    add_registration(message.from_user.id, event_id, user_name, phone_number)
    
    await message.answer(
        get_text("registration_success", lang),
        reply_markup=main_menu(lang)
    )
    await state.clear()


@router.message(RegistrationStates.waiting_for_phone, F.text)
async def get_registration_phone_text(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    
    # Handle manual phone number input
    phone_number = message.text.strip()
    
    if not phone_number:
        await message.answer(get_text("send_phone", lang))
        return
    
    data = await state.get_data()
    event_id = data.get("event_id")
    user_name = data.get("user_name")
    
    # Save registration
    add_registration(message.from_user.id, event_id, user_name, phone_number)
    
    await message.answer(
        get_text("registration_success", lang),
        reply_markup=main_menu(lang)
    )
    await state.clear()