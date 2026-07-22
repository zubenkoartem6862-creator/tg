from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    admin_ids: frozenset[int]
    channel_url: str
    database_path: Path
    log_level: str

def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN не задан в .env или переменных окружения")
    raw = os.getenv("ADMIN_IDS", "")
    ids = frozenset(int(x.strip()) for x in raw.split(",") if x.strip().lstrip("-").isdigit())
    if not ids:
        raise RuntimeError("ADMIN_IDS не задан")
    channel = os.getenv("CHANNEL_URL", "https://t.me/wh1sp3r_team").strip()
    return Settings(token, ids, channel, Path(os.getenv("DATABASE_PATH", "bot.db")), os.getenv("LOG_LEVEL", "INFO").upper())
