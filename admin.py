import asyncio
from html import escape
from aiogram import Bot,F,Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery
from aiogram.exceptions import TelegramForbiddenError,TelegramRetryAfter
from menus import panel_kb,broadcast_kb
from states import AdminReplyForm,BroadcastForm
from tools import content_info
router=Router()
def allowed(uid,settings): return uid in settings.admin_ids
@router.message(Command('admin'))
async def panel(m:Message,settings):
    if allowed(m.from_user.id,settings): await m.answer('<b>⚙️ Административная панель</b>\n\nВыберите раздел:',reply_markup=panel_kb())
@router.callback_query(F.data.startswith('panel:'))
async def section(c:CallbackQuery,state:FSMContext,database,settings):
    if not allowed(c.from_user.id,settings): await c.answer('Нет доступа.',show_alert=True); return
    await c.answer(); s=c.data.split(':')[1]
    if s=='stats':
        d=await database.stats(); await c.message.answer(f"<b>📊 Статистика</b>\n\nПользователей: <b>{d['users']}</b>\nНовых сегодня: <b>{d['today']}</b>\nАнкет: <b>{d['apps']}</b>\nПринято: <b>{d['accepted']}</b>\nОтклонено: <b>{d['rejected']}</b>\nОткрытых обращений: <b>{d['tickets']}</b>\nЗаблокировано: <b>{d['blocked']}</b>")
    elif s=='apps':
        rows=await database.pending_apps(); await c.message.answer('<b>📝 Новые анкеты</b>\n'+('\n'.join(f"#{x['id']} — {escape(x['display_name'])}, {x['age']} лет, {escape(x['roblox_username'])}" for x in rows) if rows else 'Нет новых анкет.'))
    elif s=='tickets':
        rows=await database.open_tickets(); await c.message.answer('<b>💬 Открытые обращения</b>\n'+('\n'.join(f"#{x['id']} — {escape(x['full_name'])}" for x in rows) if rows else 'Нет открытых обращений.'))
    elif s=='users':
        rows=await database.users(); await c.message.answer('<b>👥 Пользователи</b>\n'+'\n'.join(f"{'🚫' if x['is_blocked'] else '✅'} <code>{x['telegram_id']}</code> — {escape(x['full_name'])}" for x in rows))
    elif s=='blocked':
        rows=await database.blocked(); await c.message.answer('<b>🚫 Заблокированные</b>\n'+('\n'.join(f"<code>{x['user_id']}</code> — {escape(x['full_name'])}" for x in rows) if rows else 'Нет заблокированных.'))
    elif s=='broadcast': await state.set_state(BroadcastForm.content); await c.message.answer('<b>📣 Рассылка</b>\n\nОтправьте текст, фото, видео или документ. /cancel — отмена.')
    elif s=='settings': await c.message.answer(f"<b>⚙️ Настройки</b>\n\nКанал: {escape(settings.channel_url)}\nБаза: {escape(str(settings.database_path))}\nАдминистраторы: "+', '.join(f'<code>{x}</code>' for x in settings.admin_ids))
@router.callback_query(F.data.startswith('admin:app:'))
async def app_action(c:CallbackQuery,database,settings,bot:Bot):
    if not allowed(c.from_user.id,settings): return
    _,_,decision,aid,uid=c.data.split(':'); aid=int(aid); uid=int(uid); status='accepted' if decision=='accept' else 'rejected'
    if not await database.set_app_status(aid,status,c.from_user.id): await c.answer('Анкета уже обработана.',show_alert=True); return
    text='<b>🎉 Поздравляем!</b>\n\nВаша анкета была принята. Скоро владелец или администратор отправит ссылку на хаус.' if status=='accepted' else '<b>К сожалению, ваша анкета не была принята.</b>\n\nСпасибо за участие! Вы сможете попробовать снова позже.'
    try: await bot.send_message(uid,text)
    except Exception: pass
    await database.log(c.from_user.id,'application_'+status,uid,'application',aid); await c.answer('Готово.'); await c.message.edit_reply_markup(reply_markup=None); await c.message.answer(('✅ Принята' if status=='accepted' else '❌ Отклонена')+f' анкета #{aid}.')
@router.callback_query(F.data.startswith('admin:reply:'))
async def reply_start(c:CallbackQuery,state:FSMContext,settings):
    if not allowed(c.from_user.id,settings): return
    _,_,kind,uid,eid=c.data.split(':'); await state.set_state(AdminReplyForm.message); await state.update_data(uid=int(uid),kind=kind,eid=int(eid)); await c.answer(); await c.message.answer('Отправьте ответ пользователю: текст, фото, видео, документ, голосовое или стикер. /cancel — отмена.')
@router.message(AdminReplyForm.message)
async def reply_send(m:Message,state:FSMContext,database,settings,bot:Bot):
    if not allowed(m.from_user.id,settings): await state.clear(); return
    if not (m.text or m.photo or m.video or m.document or m.voice or m.sticker): await m.answer('Этот тип сообщения не поддерживается.'); return
    d=await state.get_data()
    try: await bot.send_message(d['uid'],'<b>💬 Ответ от поддержки:</b>'); sent=await m.copy_to(d['uid'])
    except Exception: await m.answer('Не удалось отправить ответ. Возможно, пользователь заблокировал бота.'); await state.clear(); return
    if d['kind']=='ticket' and d['eid']:
        ct,fid,text=content_info(m); await database.add_message(d['eid'],d['uid'],'admin',ct,sent.message_id,fid,text)
    await database.log(m.from_user.id,'reply_to_user',d['uid'],d['kind'],d['eid'] or None); await state.clear(); await m.answer('✅ Ответ отправлен.')
@router.callback_query(F.data.startswith('admin:ticket:close:'))
async def close(c:CallbackQuery,database,settings):
    if not allowed(c.from_user.id,settings): return
    _,_,_,tid,uid=c.data.split(':'); tid=int(tid); uid=int(uid)
    if not await database.close_ticket(tid,c.from_user.id): await c.answer('Уже закрыто.',show_alert=True); return
    await database.log(c.from_user.id,'close_ticket',uid,'ticket',tid); await c.answer('Закрыто.'); await c.message.edit_reply_markup(reply_markup=None); await c.message.answer(f'✅ Обращение #{tid} закрыто.')
@router.callback_query(F.data.startswith('admin:block:'))
async def block(c:CallbackQuery,database,settings,bot:Bot):
    if not allowed(c.from_user.id,settings): return
    _,_,uid,etype,eid=c.data.split(':'); uid=int(uid); eid=int(eid)
    if uid in settings.admin_ids: await c.answer('Нельзя заблокировать администратора.',show_alert=True); return
    await database.block(uid,c.from_user.id); await database.log(c.from_user.id,'block_user',uid,etype,eid)
    try: await bot.send_message(uid,'🚫 Доступ к боту ограничен администрацией.')
    except Exception: pass
    await c.answer('Пользователь заблокирован.'); await c.message.edit_reply_markup(reply_markup=None); await c.message.answer(f'🚫 Пользователь <code>{uid}</code> заблокирован.')
@router.message(BroadcastForm.content)
async def broadcast_content(m:Message,state:FSMContext,settings):
    if not allowed(m.from_user.id,settings): return
    if not (m.text or m.photo or m.video or m.document): await m.answer('Поддерживаются текст, фото, видео и документы.'); return
    await state.update_data(chat=m.chat.id,mid=m.message_id); await state.set_state(BroadcastForm.preview); await m.answer('<b>Предварительный просмотр:</b>'); await m.copy_to(m.chat.id); await m.answer('Начать рассылку?',reply_markup=broadcast_kb())
@router.callback_query(BroadcastForm.preview,F.data=='broadcast:cancel')
async def broadcast_cancel(c,state): await c.answer(); await state.clear(); await c.message.answer('Рассылка отменена.')
@router.callback_query(BroadcastForm.preview,F.data=='broadcast:start')
async def broadcast_start(c:CallbackQuery,state:FSMContext,database,settings,bot:Bot):
    if not allowed(c.from_user.id,settings): return
    await c.answer(); d=await state.get_data(); sent=blocked=errors=0; users=await database.user_ids(); progress=await c.message.answer(f'Рассылка началась. Получателей: {len(users)}')
    for uid in users:
        try: await bot.copy_message(uid,d['chat'],d['mid']); sent+=1
        except TelegramForbiddenError: blocked+=1
        except TelegramRetryAfter as e: await asyncio.sleep(e.retry_after); errors+=1
        except Exception: errors+=1
        await asyncio.sleep(.04)
    await database.log(c.from_user.id,'broadcast',details={'sent':sent,'blocked':blocked,'errors':errors}); await state.clear(); await progress.edit_text(f'<b>📣 Рассылка завершена</b>\n\nОтправлено: <b>{sent}</b>\nЗаблокировали бота: <b>{blocked}</b>\nОшибок: <b>{errors}</b>')
