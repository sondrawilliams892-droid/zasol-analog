from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.inline import back_button
from bot.services.database import get_or_create_user
from bot.services.credit_score import credit_service
from bot.models import SessionLocal

router = Router()

@router.callback_query(F.data == "menu:profile")
async def profile_handler(callback: CallbackQuery):
    db = next(SessionLocal())
    user = get_or_create_user(db, callback.from_user.id)
    
    # Get credit history count
    credit_entries = len(credit_service.get_credit_history(callback.from_user.id))
    
    text = (
        f"👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{user.telegram_id}</code>\n"
        f"📛 Имя: {user.first_name or '—'} {user.last_name or ''}\n"
        f"🔗 Username: @{user.username or '—'}\n\n"
        f"📊 Поисков: <b>{user.search_count}</b>\n"
        f"💳 Credit записей: <b>{credit_entries}</b>\n"
        f"⭐ Статус: {'Premium' if user.is_premium else 'Free'}\n\n"
        f"🕐 Регистрация: {user.created_at.strftime('%Y-%m-%d') if user.created_at else '—'}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=back_button("menu:main")
    )
    await callback.answer()
