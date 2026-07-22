from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Вступить в Whisper.team", callback_data="user:application")],
        [
            InlineKeyboardButton(text="🎧 Поддержка", callback_data="user:support"),
            InlineKeyboardButton(text="✨ О команде", callback_data="user:info"),
        ],
        [InlineKeyboardButton(text="📣 Наш Telegram-канал", url=url)],
    ])


def cancel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="↩️ Отменить и вернуться")]],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Напишите ответ…",
    )


def preview_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Отправить анкету", callback_data="app:submit")],
        [
            InlineKeyboardButton(text="✏️ Изменить ответы", callback_data="app:restart"),
            InlineKeyboardButton(text="🗑 Отменить", callback_data="app:cancel"),
        ],
    ])


def app_admin_kb(aid: int, uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"admin:app:accept:{aid}:{uid}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin:app:reject:{aid}:{uid}"),
        ],
        [InlineKeyboardButton(text="💬 Написать участнику", callback_data=f"admin:reply:user:{uid}:0")],
        [InlineKeyboardButton(text="⛔ Заблокировать", callback_data=f"admin:block:{uid}:application:{aid}")],
    ])


def ticket_admin_kb(tid: int, uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"admin:reply:ticket:{uid}:{tid}")],
        [InlineKeyboardButton(text="✅ Закрыть обращение", callback_data=f"admin:ticket:close:{tid}:{uid}")],
        [InlineKeyboardButton(text="⛔ Заблокировать", callback_data=f"admin:block:{uid}:ticket:{tid}")],
    ])


def panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 Новые анкеты", callback_data="panel:apps")],
        [InlineKeyboardButton(text="🎧 Поддержка", callback_data="panel:tickets")],
        [
            InlineKeyboardButton(text="👥 Участники", callback_data="panel:users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="panel:stats"),
        ],
        [
            InlineKeyboardButton(text="📢 Рассылка", callback_data="panel:broadcast"),
            InlineKeyboardButton(text="⛔ Блокировки", callback_data="panel:blocked"),
        ],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="panel:settings")],
    ])


def broadcast_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Запустить рассылку", callback_data="broadcast:start")],
        [InlineKeyboardButton(text="🗑 Отменить", callback_data="broadcast:cancel")],
    ])
