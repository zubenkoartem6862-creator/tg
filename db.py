from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import aiosqlite

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

class Database:
    def __init__(self, path: Path): self.path = path
    async def init(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.path) as db:
            await db.executescript('''
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS users(telegram_id INTEGER PRIMARY KEY,username TEXT,full_name TEXT NOT NULL,first_started_at TEXT NOT NULL,last_activity_at TEXT NOT NULL,is_blocked INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,display_name TEXT NOT NULL,age INTEGER NOT NULL,roblox_username TEXT NOT NULL,activity TEXT NOT NULL,tiktok_photo_id TEXT NOT NULL,skin_photo_id TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',created_at TEXT NOT NULL,reviewed_at TEXT,reviewed_by INTEGER);
            CREATE TABLE IF NOT EXISTS support_tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,status TEXT NOT NULL DEFAULT 'open',source TEXT NOT NULL,created_at TEXT NOT NULL,closed_at TEXT,closed_by INTEGER);
            CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,ticket_id INTEGER,user_id INTEGER NOT NULL,sender_role TEXT NOT NULL,content_type TEXT NOT NULL,telegram_message_id INTEGER,file_id TEXT,text_content TEXT,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS admin_actions(id INTEGER PRIMARY KEY AUTOINCREMENT,admin_id INTEGER NOT NULL,action TEXT NOT NULL,target_user_id INTEGER,entity_type TEXT,entity_id INTEGER,details TEXT,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS blocked_users(user_id INTEGER PRIMARY KEY,blocked_by INTEGER NOT NULL,reason TEXT,blocked_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_apps ON applications(user_id,status,created_at);
            CREATE INDEX IF NOT EXISTS idx_tickets ON support_tickets(status);
            ''')
            await db.commit()
    async def execute(self,q,args=()):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute(q,args); await db.commit(); return cur.lastrowid,cur.rowcount
    async def one(self,q,args=()):
        async with aiosqlite.connect(self.path) as db:
            db.row_factory=aiosqlite.Row; cur=await db.execute(q,args); row=await cur.fetchone(); return dict(row) if row else None
    async def all(self,q,args=()):
        async with aiosqlite.connect(self.path) as db:
            db.row_factory=aiosqlite.Row; cur=await db.execute(q,args); return [dict(x) for x in await cur.fetchall()]
    async def upsert_user(self,u):
        t=now(); await self.execute('''INSERT INTO users VALUES(?,?,?,?,?,0) ON CONFLICT(telegram_id) DO UPDATE SET username=excluded.username,full_name=excluded.full_name,last_activity_at=excluded.last_activity_at''',(u.id,u.username,u.full_name,t,t))
    async def is_blocked(self,uid): return bool(await self.one("SELECT 1 x FROM blocked_users WHERE user_id=?",(uid,)))
    async def block(self,uid,aid):
        await self.execute("INSERT OR REPLACE INTO blocked_users VALUES(?,?,?,?)",(uid,aid,"Заблокирован администратором",now())); await self.execute("UPDATE users SET is_blocked=1 WHERE telegram_id=?",(uid,))
    async def create_app(self,uid,d):
        x,_=await self.execute('''INSERT INTO applications(user_id,display_name,age,roblox_username,activity,tiktok_photo_id,skin_photo_id,created_at) VALUES(?,?,?,?,?,?,?,?)''',(uid,d['name'],d['age'],d['roblox'],d['activity'],d['tiktok'],d['skin'],now())); return int(x)
    async def recent_pending(self,uid):
        threshold=(datetime.now(timezone.utc)-timedelta(hours=24)).isoformat(timespec="seconds")
        return bool(await self.one("SELECT id FROM applications WHERE user_id=? AND status='pending' AND created_at>=? LIMIT 1",(uid,threshold)))
    async def app(self,aid): return await self.one("SELECT * FROM applications WHERE id=?",(aid,))
    async def set_app_status(self,aid,status,admin):
        _,n=await self.execute("UPDATE applications SET status=?,reviewed_at=?,reviewed_by=? WHERE id=? AND status='pending'",(status,now(),admin,aid)); return n>0
    async def create_ticket(self,uid,source):
        x,_=await self.execute("INSERT INTO support_tickets(user_id,source,created_at) VALUES(?,?,?)",(uid,source,now())); return int(x)
    async def add_message(self,tid,uid,role,ctype,mid,file_id,text):
        await self.execute("INSERT INTO messages(ticket_id,user_id,sender_role,content_type,telegram_message_id,file_id,text_content,created_at) VALUES(?,?,?,?,?,?,?,?)",(tid,uid,role,ctype,mid,file_id,text,now()))
    async def close_ticket(self,tid,admin):
        _,n=await self.execute("UPDATE support_tickets SET status='closed',closed_at=?,closed_by=? WHERE id=? AND status='open'",(now(),admin,tid)); return n>0
    async def log(self,admin,action,target=None,etype=None,eid=None,details=None):
        if isinstance(details,dict): details=json.dumps(details,ensure_ascii=False)
        await self.execute("INSERT INTO admin_actions(admin_id,action,target_user_id,entity_type,entity_id,details,created_at) VALUES(?,?,?,?,?,?,?)",(admin,action,target,etype,eid,details,now()))
    async def stats(self):
        qs={"users":"SELECT COUNT(*) n FROM users","today":"SELECT COUNT(*) n FROM users WHERE substr(first_started_at,1,10)=?","apps":"SELECT COUNT(*) n FROM applications","accepted":"SELECT COUNT(*) n FROM applications WHERE status='accepted'","rejected":"SELECT COUNT(*) n FROM applications WHERE status='rejected'","tickets":"SELECT COUNT(*) n FROM support_tickets WHERE status='open'","blocked":"SELECT COUNT(*) n FROM blocked_users"}; out={}; today=datetime.now(timezone.utc).date().isoformat()
        for k,q in qs.items(): out[k]=(await self.one(q,(today,) if k=='today' else ()))['n']
        return out
    async def pending_apps(self): return await self.all("SELECT * FROM applications WHERE status='pending' ORDER BY id DESC LIMIT 20")
    async def open_tickets(self): return await self.all("SELECT t.*,u.full_name,u.username FROM support_tickets t JOIN users u ON u.telegram_id=t.user_id WHERE t.status='open' ORDER BY t.id DESC LIMIT 20")
    async def users(self): return await self.all("SELECT * FROM users ORDER BY last_activity_at DESC LIMIT 30")
    async def blocked(self): return await self.all("SELECT b.*,u.full_name,u.username FROM blocked_users b JOIN users u ON u.telegram_id=b.user_id ORDER BY blocked_at DESC LIMIT 30")
    async def user_ids(self): return [x['telegram_id'] for x in await self.all("SELECT telegram_id FROM users WHERE is_blocked=0")]
