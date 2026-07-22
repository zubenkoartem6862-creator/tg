from aiogram import F,Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery,ReplyKeyboardRemove
from menus import main_menu
from texts import START,INFO,HELP
router=Router()
@router.message(Command('start'))
@router.message(Command('menu'))
async def menu(m:Message,state:FSMContext,settings):
    await state.clear(); await m.answer(START,reply_markup=main_menu(settings.channel_url))
@router.message(Command('help'))
async def help_cmd(m:Message,settings): await m.answer(HELP,reply_markup=main_menu(settings.channel_url))
@router.message(Command('id'))
async def id_cmd(m:Message): await m.answer(f'Ваш Telegram ID: <code>{m.from_user.id}</code>')
@router.message(Command('cancel'))
@router.message(F.text=='↩️ Отменить и вернуться')
async def cancel(m:Message,state:FSMContext,settings):
    await state.clear(); await m.answer('Действие отменено.',reply_markup=ReplyKeyboardRemove()); await m.answer(START,reply_markup=main_menu(settings.channel_url))
@router.callback_query(F.data=='user:info')
async def info(c:CallbackQuery,settings):
    await c.answer(); await c.message.answer(INFO.format(url=settings.channel_url),reply_markup=main_menu(settings.channel_url))
