from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🔍 Phone Lookup", callback_data="menu:phone")],
        [InlineKeyboardButton(text="📦 Batch Lookup", callback_data="menu:batch")],
        [InlineKeyboardButton(text="💰 Credit Score", callback_data="menu:credit")],
        [InlineKeyboardButton(text="📋 Credit Report", callback_data="menu:credit_report")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="menu:profile")],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="menu:support")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def phone_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🔍 Новый поиск", callback_data="phone:new")],
        [InlineKeyboardButton(text="📜 История", callback_data="phone:history")],
        [InlineKeyboardButton(text="📦 Batch Search", callback_data="phone:batch")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def credit_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🔗 Бесплатные сервисы", callback_data="credit:services")],
        [InlineKeyboardButton(text="📝 Добавить свой скор", callback_data="credit:add")],
        [InlineKeyboardButton(text="📜 История", callback_data="credit:history")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_button(callback: str = "menu:main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=callback)]
    ])

def cancel_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
