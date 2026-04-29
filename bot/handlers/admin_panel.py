from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import Command

from bot.config import ADMIN_IDS
from bot.models import SessionLocal, User, PhoneSearch

router = Router()

@router.message(Command("admin"))
async def cmd_admin(message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа.")
        return
    
    db = next(SessionLocal())
    total_users = db.query(User).count()
    total_searches = db.query(PhoneSearch).count()
    premium_users = db.query(User).filter(User.is_premium == 1).count()
    
    text = (
        f"🔐 <b>Админ-панель</b>\n\n"
        f"👥 Всего пользователей: <b>{total_users}</b>\n"
        f"🔍 Всего поисков: <b>{total_searches}</b>\n"
        f"⭐ Premium: <b>{premium_users}</b>\n"
    )
    
    await message.answer(text)

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    db = next(SessionLocal())
    total_users = db.query(User).count()
    total_searches = db.query(PhoneSearch).count()
    
    await callback.message.edit_text(
        f"📊 Статистика:\n\n"
        f"Пользователей: {total_users}\n"
        f"Поисков: {total_searches}",
    )
    await callback.answer()
