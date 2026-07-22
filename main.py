from __future__ import annotations
import asyncio,logging,sys
from aiogram import Bot,Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import load_settings
from database import Database
from handlers import register_routers
from middlewares import AccessMiddleware,SpamMiddleware

async def main():
    settings=load_settings()
    logging.basicConfig(level=getattr(logging,settings.log_level,logging.INFO),format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',handlers=[logging.StreamHandler(sys.stdout)])
    db=Database(settings.database_path); await db.init()
    bot=Bot(settings.bot_token,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp=Dispatcher(storage=MemoryStorage()); dp['settings']=settings; dp['database']=db
    for observer in (dp.message,dp.callback_query):
        observer.outer_middleware(AccessMiddleware(db,settings.admin_ids)); observer.outer_middleware(SpamMiddleware(settings.admin_ids))
    register_routers(dp)
    await bot.set_my_commands([BotCommand(command='start',description='Запустить бота'),BotCommand(command='menu',description='Главное меню'),BotCommand(command='help',description='Помощь'),BotCommand(command='cancel',description='Отменить действие'),BotCommand(command='id',description='Узнать Telegram ID')])
    logging.info('Бот Whisper.team запущен')
    try: await dp.start_polling(bot,settings=settings,database=db,allowed_updates=dp.resolve_used_update_types())
    finally: await bot.session.close()

if __name__=='__main__': asyncio.run(main())
