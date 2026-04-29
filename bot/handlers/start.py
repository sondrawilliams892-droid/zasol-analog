from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import main_menu, back_button
from bot.services.database import get_or_create_user, increment_search_count
from bot.models import SessionLocal

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    db = next(SessionLocal())
    user = get_or_create_user(
        db, 
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    text = (
        f"👋 Привет, {message.from_user.first_name or 'друг'}!\n\n"
        f"🔍 <b>Zasol Analog</b> — легальный инструмент:\n"
        f"• Reverse Phone Lookup (Whitepages API / скрепинг)\n"
        f"• Credit Score трекер (самоотчёт + история)\n\n"
        f"📊 Ваших поисков: {user.search_count}\n\n"
        f"⚠️ <i>Все данные из публичных источников.</i>\n"
        f"<i>Credit Score — только ваш собственный.</i>"
    )
    
    await message.answer(text, reply_markup=main_menu())

@router.callback_query(F.data == "menu:main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🔍 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "menu:support")
async def support(callback: CallbackQuery):
    await callback.message.edit_text(
        "💬 <b>Поддержка</b>\n\n"
        "Если у вас вопросы или проблемы — напишите @ваш_админ\n\n"
        "📧 Email: support@example.com",
        reply_markup=back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено.",
        reply_markup=main_menu()
    )
    await callback.answer("Отменено")
