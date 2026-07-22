import time
from collections import defaultdict,deque
from aiogram import BaseMiddleware
from aiogram.types import Message,CallbackQuery
from texts import BLOCKED

class AccessMiddleware(BaseMiddleware):
    def __init__(self,db,admins): self.db=db; self.admins=admins
    async def __call__(self,handler,event,data):
        u=data.get('event_from_user')
        if not u:return await handler(event,data)
        await self.db.upsert_user(u)
        if u.id not in self.admins and await self.db.is_blocked(u.id):
            if isinstance(event,Message): await event.answer(BLOCKED)
            elif isinstance(event,CallbackQuery): await event.answer(BLOCKED,show_alert=True)
            return
        return await handler(event,data)
class SpamMiddleware(BaseMiddleware):
    def __init__(self,admins): self.admins=admins; self.q=defaultdict(deque)
    async def __call__(self,handler,event,data):
        u=data.get('event_from_user')
        if not u or u.id in self.admins:return await handler(event,data)
        now=time.monotonic(); q=self.q[u.id]
        while q and now-q[0]>60:q.popleft()
        if len(q)>=5:
            text='⏳ Слишком много сообщений. Подождите одну минуту.'
            if isinstance(event,Message):await event.answer(text)
            else:await event.answer(text,show_alert=True)
            return
        q.append(now); return await handler(event,data)
