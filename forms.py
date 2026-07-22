from aiogram.fsm.state import State, StatesGroup

class ApplicationForm(StatesGroup):
    name = State(); age = State(); roblox = State(); activity = State(); tiktok = State(); skin = State(); preview = State()

class SupportForm(StatesGroup):
    message = State()

class AdminReplyForm(StatesGroup):
    message = State()

class BroadcastForm(StatesGroup):
    content = State(); preview = State()
