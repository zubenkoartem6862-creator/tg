from datetime import datetime
from html import escape
from aiogram import Bot,F,Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery,InputMediaPhoto,ReplyKeyboardRemove
from menus import cancel_menu,preview_kb,app_admin_kb,main_menu
from states import ApplicationForm
from tools import profile
router=Router()
async def begin(m,state,db):
    if await db.recent_pending(m.from_user.id):
        await m.answer('⏳ У вас уже есть анкета на рассмотрении. Повторная отправка доступна через 24 часа.'); return
    await state.clear(); await state.set_state(ApplicationForm.name); await m.answer('<b>Шаг 1 из 6</b>\n\nКак вас зовут или какой у вас псевдоним?',reply_markup=cancel_menu())
@router.callback_query(F.data=='user:application')
async def start(c:CallbackQuery,state:FSMContext,database): await c.answer(); await begin(c.message,state,database)
@router.message(ApplicationForm.name,F.text)
async def name(m:Message,state:FSMContext):
    v=m.text.strip()
    if not 2<=len(v)<=60: await m.answer('Введите от 2 до 60 символов.'); return
    await state.update_data(name=v); await state.set_state(ApplicationForm.age); await m.answer('<b>Шаг 2 из 6</b>\n\nСколько вам лет?')
@router.message(ApplicationForm.name)
async def name_bad(m:Message): await m.answer('Отправьте имя обычным текстом.')
@router.message(ApplicationForm.age,F.text)
async def age(m:Message,state:FSMContext):
    if not m.text.strip().isdigit(): await m.answer('Возраст должен быть числом.'); return
    v=int(m.text)
    if v<10: await m.answer('Минимальный возраст — 10 лет.'); return
    if v>99: await m.answer('Проверьте возраст.'); return
    await state.update_data(age=v); await state.set_state(ApplicationForm.roblox); await m.answer('<b>Шаг 3 из 6</b>\n\nНапишите никнейм в Roblox.')
@router.message(ApplicationForm.age)
async def age_bad(m:Message): await m.answer('Отправьте возраст числом.')
@router.message(ApplicationForm.roblox,F.text)
async def roblox(m:Message,state:FSMContext):
    v=m.text.strip()
    if not 3<=len(v)<=40: await m.answer('Никнейм должен содержать 3–40 символов.'); return
    await state.update_data(roblox=v); await state.set_state(ApplicationForm.activity); await m.answer('<b>Шаг 4 из 6</b>\n\nНасколько вы активны? Например: каждый день или несколько раз в неделю.')
@router.message(ApplicationForm.activity,F.text)
async def activity(m:Message,state:FSMContext):
    v=m.text.strip()
    if not 3<=len(v)<=300: await m.answer('Опишите активность текстом до 300 символов.'); return
    await state.update_data(activity=v); await state.set_state(ApplicationForm.tiktok); await m.answer('<b>Шаг 5 из 6</b>\n\nОтправьте фотографией скриншот TikTok.')
@router.message(ApplicationForm.tiktok,F.photo)
async def tiktok(m:Message,state:FSMContext):
    await state.update_data(tiktok=m.photo[-1].file_id); await state.set_state(ApplicationForm.skin); await m.answer('<b>Шаг 6 из 6</b>\n\nОтправьте фотографией скриншот скина Roblox.')
@router.message(ApplicationForm.tiktok)
async def tiktok_bad(m:Message): await m.answer('Нужно отправить именно фотографию.')
@router.message(ApplicationForm.skin,F.photo)
async def skin(m:Message,state:FSMContext):
    await state.update_data(skin=m.photo[-1].file_id); d=await state.get_data(); await state.set_state(ApplicationForm.preview)
    await m.answer(f"<b>Проверьте анкету</b>\n\n<b>Имя:</b> {escape(d['name'])}\n<b>Возраст:</b> {d['age']}\n<b>Roblox:</b> {escape(d['roblox'])}\n<b>Активность:</b> {escape(d['activity'])}",reply_markup=ReplyKeyboardRemove())
    await m.answer_media_group([InputMediaPhoto(media=d['tiktok'],caption='Скриншот TikTok'),InputMediaPhoto(media=d['skin'],caption='Скриншот скина Roblox')]); await m.answer('Всё правильно?',reply_markup=preview_kb())
@router.message(ApplicationForm.skin)
async def skin_bad(m:Message): await m.answer('Нужно отправить именно фотографию.')
@router.callback_query(ApplicationForm.preview,F.data=='app:restart')
async def restart(c,state,database): await c.answer(); await begin(c.message,state,database)
@router.callback_query(ApplicationForm.preview,F.data=='app:cancel')
async def cancel(c,state,settings): await c.answer(); await state.clear(); await c.message.answer('Анкета отменена.',reply_markup=main_menu(settings.channel_url))
@router.callback_query(ApplicationForm.preview,F.data=='app:submit')
async def submit(c:CallbackQuery,state:FSMContext,database,settings,bot:Bot):
    await c.answer()
    if await database.recent_pending(c.from_user.id): await state.clear(); await c.message.answer('У вас уже есть анкета на рассмотрении.'); return
    d=await state.get_data(); aid=await database.create_app(c.from_user.id,d); app=await database.app(aid); username=f'@{c.from_user.username}' if c.from_user.username else 'не указан'; created=datetime.fromisoformat(app['created_at']).astimezone().strftime('%d.%m.%Y %H:%M:%S')
    text=f"<b>📝 Новая анкета #{aid}</b>\n\n<b>Имя:</b> {escape(d['name'])}\n<b>Возраст:</b> {d['age']}\n<b>Roblox:</b> {escape(d['roblox'])}\n<b>Активность:</b> {escape(d['activity'])}\n\n<b>Username:</b> {escape(username)}\n<b>Telegram ID:</b> <code>{c.from_user.id}</code>\n<b>Профиль:</b> {profile(c.from_user.id,c.from_user.full_name)}\n<b>Дата:</b> {created}"
    for admin in settings.admin_ids:
        try:
            await bot.send_message(admin,text,reply_markup=app_admin_kb(aid,c.from_user.id)); await bot.send_media_group(admin,[InputMediaPhoto(media=d['tiktok'],caption=f'TikTok — анкета #{aid}'),InputMediaPhoto(media=d['skin'],caption=f'Скин Roblox — анкета #{aid}')])
        except Exception: pass
    await state.clear(); await c.message.answer('<b>✅ Ваша анкета успешно отправлена!</b>\n\nАдминистрация рассмотрит её. Если вы подойдёте, вам отправят ссылку на хаус. Если в течение 24 часов вам не написали, анкета не была принята.',reply_markup=main_menu(settings.channel_url))
