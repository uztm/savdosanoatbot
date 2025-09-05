from aiogram import Router, types
from keyboards import events_keyboard
from database import get_event_detail

router = Router()


@router.message(lambda m: m.text == "📅 Tadbirlar ro'yxati")
async def show_events(message: types.Message):
    kb = events_keyboard()
    if kb and kb.inline_keyboard:
        await message.answer("📅 Tadbirlar ro'yxati:", reply_markup=kb)
    else:
        await message.answer("📭 Hozircha tadbirlar yo‘q.")


@router.callback_query(lambda c: c.data.startswith("event_"))
async def event_detail(callback: types.CallbackQuery):
    try:
        event_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        return await callback.answer("❌ Noto‘g‘ri event ID", show_alert=True)

    event = get_event_detail(event_id)

    if not event:
        await callback.message.answer("❌ Tadbir topilmadi.")
        return await callback.answer()

    title, desc, image_url = event
    caption = f"<b>{title}</b>\n\n{desc}"

    if image_url:
        try:
            await callback.message.answer_photo(
                photo=image_url,
                caption=caption,
                parse_mode="HTML"
            )
        except Exception:
            # Agar rasm ID noto‘g‘ri bo‘lsa, faqat text chiqsin
            await callback.message.answer(caption, parse_mode="HTML")
    else:
        await callback.message.answer(caption, parse_mode="HTML")

    await callback.answer()
