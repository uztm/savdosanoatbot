from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile
from config import ADMIN_IDS
from database import (
    add_event, get_user_language, get_all_users, archive_event,
    get_events, get_event_registrations, export_registrations_to_excel,
    get_event_detail, update_event
)
from keyboards import admin_panel_keyboard, manage_events_keyboard, event_management_keyboard
from translations import get_text

router = Router()


# --- STATE MACHINES ---
class AddEventStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_image = State()
    waiting_for_description = State()
    waiting_for_link = State()


class EditEventStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_image = State()
    waiting_for_description = State()
    waiting_for_link = State()


class MessageStates(StatesGroup):
    waiting_for_message = State()


# --- ADMIN PANEL ---
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        lang = get_user_language(message.from_user.id)
        return await message.answer(get_text("not_admin", lang))
    
    lang = get_user_language(message.from_user.id)
    kb = admin_panel_keyboard(lang)
    await message.answer(get_text("admin_panel", lang), reply_markup=kb)


# --- ADD EVENT ---
@router.callback_query(F.data == "admin_add")
async def admin_add_event(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        lang = get_user_language(callback.from_user.id)
        return await callback.answer(get_text("not_admin", lang), show_alert=True)

    lang = get_user_language(callback.from_user.id)
    await callback.message.answer(get_text("enter_title", lang))
    await state.set_state(AddEventStates.waiting_for_title)
    await callback.answer()


@router.message(AddEventStates.waiting_for_title, F.text)
async def get_event_title(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    title = message.text.strip()
    await state.update_data(title=title)
    await message.answer(get_text("send_image", lang))
    await state.set_state(AddEventStates.waiting_for_image)


@router.message(AddEventStates.waiting_for_image, F.photo)
async def get_event_image(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    photo_id = message.photo[-1].file_id
    await state.update_data(image=photo_id)
    await message.answer(get_text("enter_description", lang))
    await state.set_state(AddEventStates.waiting_for_description)


@router.message(AddEventStates.waiting_for_description, F.text)
async def get_event_description(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    description = message.text.strip()
    await state.update_data(description=description)
    await message.answer(get_text("enter_link", lang))
    await state.set_state(AddEventStates.waiting_for_link)


@router.message(AddEventStates.waiting_for_link)
async def get_event_link(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    
    if message.text and message.text.strip() == get_text("skip", lang):
        link = None
    else:
        link = message.text.strip() if message.text else None

    data = await state.get_data()
    title = data.get("title")
    image = data.get("image")
    description = data.get("description")

    # Add event to database
    add_event(title=title, description=description, image_url=image, read_more_link=link)

    await message.answer(get_text("event_added", lang))
    await state.clear()


# --- MANAGE EVENTS ---
@router.callback_query(F.data == "admin_manage")
async def admin_manage_events(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        lang = get_user_language(callback.from_user.id)
        return await callback.answer(get_text("not_admin", lang), show_alert=True)

    lang = get_user_language(callback.from_user.id)
    kb = manage_events_keyboard()
    
    if kb and kb.inline_keyboard:
        await callback.message.answer(get_text("choose_event_manage", lang), reply_markup=kb)
    else:
        await callback.message.answer(get_text("no_events", lang))
    
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("manage_"))
async def show_event_management(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        lang = get_user_language(callback.from_user.id)
        return await callback.answer(get_text("not_admin", lang), show_alert=True)

    try:
        event_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        return await callback.answer("❌ Invalid event ID", show_alert=True)

    lang = get_user_language(callback.from_user.id)
    event = get_event_detail(event_id)
    
    if not event:
        await callback.message.answer(get_text("event_not_found", lang))
        return await callback.answer()

    title = event[0]
    kb = event_management_keyboard(event_id, lang)
    
    await callback.message.answer(
        f"📊 Managing event: <b>{title}</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


# --- ARCHIVE EVENT ---
@router.callback_query(lambda c: c.data.startswith("archive_"))
async def archive_event_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        lang = get_user_language(callback.from_user.id)
        return await callback.answer(get_text("not_admin", lang), show_alert=True)

    try:
        event_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        return await callback.answer("❌ Invalid event ID", show_alert=True)

    lang = get_user_language(callback.from_user.id)
    archive_event(event_id)
    
    await callback.message.answer(get_text("event_archived", lang))
    await callback.answer()


# --- DOWNLOAD REGISTRATIONS ---
@router.callback_query(lambda c: c.data.startswith("download_"))
async def download_registrations(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        lang = get_user_language(callback.from_user.id)
        return await callback.answer(get_text("not_admin", lang), show_alert=True)

    try:
        event_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        return await callback.answer("❌ Invalid event ID", show_alert=True)

    lang = get_user_language(callback.from_user.id)
    registrations = get_event_registrations(event_id)
    
    if not registrations:
        await callback.message.answer(get_text("no_registrations", lang))
        return await callback.answer()

    # Generate Excel file
    excel_file = export_registrations_to_excel(event_id)
    event = get_event_detail(event_id)
    filename = f"registrations_{event[0] if event else 'event'}.xls"
    
    # Send file
    file = BufferedInputFile(excel_file.getvalue(), filename=filename)
    await callback.message.answer_document(file)
    await callback.answer()


# --- SEND MESSAGE TO ALL USERS ---
@router.callback_query(F.data == "admin_message")
async def admin_send_message(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        lang = get_user_language(callback.from_user.id)
        return await callback.answer(get_text("not_admin", lang), show_alert=True)

    lang = get_user_language(callback.from_user.id)
    await callback.message.answer(get_text("enter_message", lang))
    await state.set_state(MessageStates.waiting_for_message)
    await callback.answer()


@router.message(MessageStates.waiting_for_message)
async def send_message_to_all(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    lang = get_user_language(message.from_user.id)
    users = get_all_users()
    sent_count = 0
    
    for user_id, user_name in users:
        try:
            if message.photo:
                await message.bot.send_photo(
                    user_id, 
                    message.photo[-1].file_id,
                    caption=message.caption
                )
            else:
                await message.bot.send_message(user_id, message.text)
            sent_count += 1
        except Exception:
            # User blocked bot or deleted account
            continue
    
    await message.answer(get_text("message_sent", lang, count=sent_count))
    await state.clear()


# --- EDIT EVENT (Optional - basic implementation) ---
@router.callback_query(lambda c: c.data.startswith("edit_"))
async def edit_event_handler(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        lang = get_user_language(callback.from_user.id)
        return await callback.answer(get_text("not_admin", lang), show_alert=True)

    try:
        event_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        return await callback.answer("❌ Invalid event ID", show_alert=True)

    lang = get_user_language(callback.from_user.id)
    await state.update_data(edit_event_id=event_id)
    await callback.message.answer(get_text("enter_title", lang))
    await state.set_state(EditEventStates.waiting_for_title)
    await callback.answer()


@router.message(EditEventStates.waiting_for_title, F.text)
async def edit_event_title(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    title = message.text.strip()
    await state.update_data(edit_title=title)
    await message.answer(get_text("send_image", lang))
    await state.set_state(EditEventStates.waiting_for_image)


@router.message(EditEventStates.waiting_for_image, F.photo)
async def edit_event_image(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    photo_id = message.photo[-1].file_id
    await state.update_data(edit_image=photo_id)
    await message.answer(get_text("enter_description", lang))
    await state.set_state(EditEventStates.waiting_for_description)


@router.message(EditEventStates.waiting_for_description, F.text)
async def edit_event_description(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    description = message.text.strip()
    await state.update_data(edit_description=description)
    await message.answer(get_text("enter_link", lang))
    await state.set_state(EditEventStates.waiting_for_link)


@router.message(EditEventStates.waiting_for_link)
async def edit_event_link(message: types.Message, state: FSMContext):
    lang = get_user_language(message.from_user.id)
    
    if message.text and message.text.strip() == get_text("skip", lang):
        link = None
    else:
        link = message.text.strip() if message.text else None

    data = await state.get_data()
    event_id = data.get("edit_event_id")
    title = data.get("edit_title")
    image = data.get("edit_image")
    description = data.get("edit_description")

    # Update event in database
    update_event(event_id, title=title, description=description, image_url=image, read_more_link=link)

    await message.answer(get_text("event_added", lang))  # Reusing the same text
    await state.clear()