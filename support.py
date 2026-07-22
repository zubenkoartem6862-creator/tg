from datetime import datetime
from html import escape
from aiogram import Bot,F,Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery
from menus import cancel_menu,main_menu,ticket_admin_kb
from states import SupportForm
from texts import SUPPORT
from tools import content_info,profile
router=Router()
SUPPORTED=F.text|F.photo|F.video|F.document|F.voice|F.sticker
async def deliver(m,database,settings,bot,source):
    tid=await database.create_ticket(m.from_user.id,source); ctype,fid,text=content_info(m); await database.add_message(tid,m.from_user.id,'user',ctype,m.message_id,fid,text)
    username=f'@{m.from_user.username}' if m.from_user.username else 'не указан'; stamp=datetime.now().astimezone().strftime('%d.%m.%Y %H:%M:%S')
    header=f"<b>💬 Новое обращение #{tid}</b>\n\n<b>Пользователь:</b> {profile(m.from_user.id,m.from_user.full_name)}\n<b>Имя:</b> {escape(m.from_user.full_name)}\n<b>Username:</b> {escape(username)}\n<b>Telegram ID:</b> <code>{m.from_user.id}</code>\n<b>Источник:</b> {'Поддержка' if source=='support' else 'Обычное сообщение'}\n<b>Дата:</b> {stamp}"
    for admin in settings.admin_ids:
        try: await bot.send_message(admin,header,reply_markup=ticket_admin_kb(tid,m.from_user.id)); await m.copy_to(admin)
        except Exception: pass
@router.callback_query(F.data=='user:support')
async def start(c:CallbackQuery,state:FSMContext): await c.answer(); await state.set_state(SupportForm.message); await c.message.answer(SUPPORT,reply_markup=cancel_menu())
@router.message(SupportForm.message,SUPPORTED)
async def receive(m:Message,state:FSMContext,database,settings,bot:Bot):
    await deliver(m,database,settings,bot,'support'); await state.clear(); await m.answer('<b>✅ Ваше сообщение передано модераторам.</b>\n\nОжидайте ответ через этого бота.',reply_markup=main_menu(settings.channel_url))
@router.message(SupportForm.message)
async def unsupported(m:Message): await m.answer('Можно отправить текст, фото, видео, документ, голосовое сообщение или стикер.')
@router.message(SUPPORTED)
async def ordinary(m:Message,database,settings,bot:Bot):
    if m.text and m.text.startswith('/'): return
    await deliver(m,database,settings,bot,'ordinary'); await m.answer('<b>✅ Ваше сообщение получено и передано модераторам.</b>\n\nОни смогут ответить вам через этого бота.',reply_markup=main_menu(settings.channel_url))
