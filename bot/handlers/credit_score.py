from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.inline import credit_menu, back_button, cancel_button
from bot.services.credit_score import credit_service
from bot.services.database import save_credit_score
from bot.models import SessionLocal

router = Router()

class CreditStates(StatesGroup):
    waiting_for_score = State()

@router.callback_query(F.data == "menu:credit")
async def credit_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "💰 <b>Credit Score</b>\n\n"
        "Проверяйте и отслеживайте свой кредитный рейтинг.\n"
        "⚠️ <i>Только ваш собственный скоринг.</i>",
        reply_markup=credit_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "credit:services")
async def credit_services(callback: CallbackQuery):
    text = credit_service.get_services_text()
    await callback.message.edit_text(
        text,
        reply_markup=back_button("menu:credit"),
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "credit:add")
async def credit_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreditStates.waiting_for_score)
    await callback.message.edit_text(
        "📝 <b>Добавить Credit Score</b>\n\n"
        "Введите в формате:\n"
        "<code>720 Experian</code>\n"
        "или\n"
        "<code>690 TransUnion Ежемесячная проверка</code>\n\n"
        "<i>Сначала число, потом бюро, потом заметка (опционально)</i>",
        reply_markup=cancel_button()
    )
    await callback.answer()

@router.message(CreditStates.waiting_for_score)
async def process_credit_score(message: Message, state: FSMContext):
    parts = message.text.strip().split(maxsplit=2)
    
    if len(parts) < 2:
        await message.answer(
            "❌ Неверный формат. Пример: <code>720 Experian</code>",
            reply_markup=back_button("menu:credit")
        )
        await state.clear()
        return
    
    try:
        score = int(parts[0])
        if not 300 <= score <= 850:
            raise ValueError
    except ValueError:
        await message.answer(
            "❌ Скор должен быть числом от 300 до 850.",
            reply_markup=back_button("menu:credit")
        )
        await state.clear()
        return
    
    bureau = parts[1]
    note = parts[2] if len(parts) > 2 else ""
    
    with SessionLocal() as db:
        save_credit_score(db, message.from_user.id, score, bureau, note)
    
    rating = credit_service.interpret_score(score)
    
    await message.answer(
        f"✅ <b>Сохранено!</b>\n\n"
        f"💯 Скор: <b>{score}</b>\n"
        f"{rating}\n"
        f"🏢 Бюро: {bureau}\n"
        f"📝 Заметка: {note or '—'}",
        reply_markup=back_button("menu:credit")
    )
    await state.clear()

@router.callback_query(F.data == "credit:history")
async def credit_history(callback: CallbackQuery):
    text = credit_service.get_history_text(callback.from_user.id)
    await callback.message.edit_text(
        text,
        reply_markup=back_button("menu:credit")
    )
    await callback.answer()

@router.callback_query(F.data == "menu:credit_report")
async def credit_report(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 <b>Credit Report</b>\n\n"
        "Получите официальный бесплатный отчёт:\n"
        "• <a href='https://www.annualcreditreport.com'>AnnualCreditReport.com</a> — законное право 1/год\n"
        "• <a href='https://www.experian.com'>Experian</a> — бесплатный Experian отчёт\n"
        "• <a href='https://www.creditkarma.com'>Credit Karma</a> — еженедельные обновления\n\n"
        "⚠️ <i>Никогда не платите за 'credit report' — официальные сервисы бесплатны.</i>",
        reply_markup=back_button("menu:main"),
        disable_web_page_preview=True
    )
    await callback.answer()
