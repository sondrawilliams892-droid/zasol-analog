from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.inline import phone_menu, back_button, cancel_button
from bot.services.phone_lookup import phone_service
from bot.services.database import get_or_create_user, increment_search_count, save_phone_search, get_user_search_history
from bot.models import SessionLocal

router = Router()

class PhoneStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_batch = State()

@router.callback_query(F.data == "menu:phone")
async def phone_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔍 <b>Phone Lookup</b>\n\n"
        "Введите номер телефона в формате +1XXXXXXXXXX\n"
        "Или используйте кнопки ниже.",
        reply_markup=phone_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "phone:new")
async def phone_new(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PhoneStates.waiting_for_phone)
    await callback.message.edit_text(
        "📱 Введите номер телефона:\n"
        "<i>Пример: +14158586273</i>",
        reply_markup=cancel_button()
    )
    await callback.answer()

@router.message(PhoneStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    
    await state.clear()
    processing_msg = await message.answer("🔍 Ищу информацию...")
    
    db = next(SessionLocal())
    increment_search_count(db, message.from_user.id)
    
    result = await phone_service.lookup(phone)
    
    if result:
        save_phone_search(db, message.from_user.id, phone, result)
    
    text = phone_service.format_result(result)
    
    await processing_msg.delete()
    await message.answer(text, reply_markup=back_button("menu:phone"))

@router.callback_query(F.data == "phone:history")
async def phone_history(callback: CallbackQuery):
    db = next(SessionLocal())
    history = get_user_search_history(db, callback.from_user.id, limit=10)
    
    if not history:
        await callback.message.edit_text(
            "📭 История пуста.",
            reply_markup=phone_menu()
        )
        await callback.answer()
        return
    
    lines = ["<b>📜 Последние поиски:</b>\n"]
    for h in history:
        lines.append(f"📞 {h.phone_number}")
        if h.result_name:
            lines.append(f"   👤 {h.result_name}")
        lines.append(f"   🕐 {h.created_at.strftime('%Y-%m-%d %H:%M')}\n")
    
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=phone_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "phone:batch")
async def phone_batch(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PhoneStates.waiting_for_batch)
    await callback.message.edit_text(
        "📦 <b>Batch Phone Lookup</b>\n\n"
        "Введите номера телефонов, по одному на строку:\n"
        "<i>Максимум 5 номеров за раз</i>",
        reply_markup=cancel_button()
    )
    await callback.answer()

@router.message(PhoneStates.waiting_for_batch)
async def process_batch(message: Message, state: FSMContext):
    lines = message.text.strip().split("\n")
    phones = [p.strip() for p in lines if p.strip()][:5]
    
    if not phones:
        await message.answer("❌ Не найдено номеров. Попробуйте снова.", reply_markup=back_button("menu:phone"))
        await state.clear()
        return
    
    await state.clear()
    db = next(SessionLocal())
    
    results = []
    total = len(phones)
    
    progress_msg = await message.answer(f"⏳ Обработка: 0/{total}")
    
    for i, phone in enumerate(phones, 1):
        await progress_msg.edit_text(f"⏳ Обработка: {i}/{total}\n📞 {phone}")
        
        increment_search_count(db, message.from_user.id)
        result = await phone_service.lookup(phone)
        
        if result:
            save_phone_search(db, message.from_user.id, phone, result)
        
        results.append((phone, result))
    
    await progress_msg.delete()
    
    # Send results
    for phone, result in results:
        text = phone_service.format_result(result)
        await message.answer(text)
    
    await message.answer(
        f"✅ Готово! Обработано {total} номеров.",
        reply_markup=back_button("menu:phone")
    )

@router.callback_query(F.data == "menu:batch")
async def menu_batch(callback: CallbackQuery, state: FSMContext):
    await phone_batch(callback, state)
