# Telegram-бот команды Whisper.team

Готовый бот на Python 3.12, aiogram 3 и SQLite для набора участников в Roblox-команду.

## Возможности

Анкеты с предварительным просмотром, поддержка вложений, ответы администрации без раскрытия аккаунта администратора, обычные сообщения с автоматической передачей модераторам, принятие и отклонение анкет, блокировки, статистика, списки пользователей и обращений, рассылка, защита от спама и сохранение данных в SQLite.

## Структура

```text
main.py
config.py
handlers/
keyboards/
database/
states/
middlewares/
utils/
requirements.txt
.env.example
.gitignore
railway.json
Procfile
```

## 1. Установка Python

Установите Python 3.12 с официального сайта Python. На Windows при установке включите `Add Python to PATH`.

Проверка:

```bash
python --version
```

## 2. Установка зависимостей

Откройте терминал в папке проекта:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Затем:

```bash
pip install -r requirements.txt
```

## 3. Создание бота через BotFather

1. Откройте официального `@BotFather` в Telegram.
2. Отправьте `/newbot`.
3. Укажите название и username, заканчивающийся на `bot`.
4. Скопируйте токен.

Токен нельзя публиковать. При утечке отзовите его через BotFather и создайте новый.

## 4. Файл `.env`

Скопируйте `.env.example`, назовите копию `.env` и заполните:

```env
BOT_TOKEN=ВАШ_НОВЫЙ_ТОКЕН
ADMIN_IDS=123456789,987654321
CHANNEL_URL=https://t.me/wh1sp3r_team
DATABASE_PATH=bot.db
LOG_LEVEL=INFO
```

## 5. Telegram ID администратора

Запустите бота и отправьте `/id`. ID выглядит как число. Для двух или нескольких администраторов укажите ID через запятую:

```env
ADMIN_IDS=123456789,987654321,555666777
```

Каждый администратор должен открыть бота и нажать `/start`, иначе Telegram не позволит боту первым написать ему.

## 6. Локальный запуск

```bash
python main.py
```

Команды: `/start`, `/menu`, `/help`, `/cancel`, `/id`. Админ-панель: `/admin`.

## 7. Railway

Не загружайте ZIP единственным файлом. Распакуйте архив и загрузите на GitHub отдельные файлы и папки проекта.

В Railway добавьте Variables:

```env
BOT_TOKEN=...
ADMIN_IDS=123456789,987654321
CHANNEL_URL=https://t.me/wh1sp3r_team
DATABASE_PATH=/data/bot.db
LOG_LEVEL=INFO
```

Команда запуска уже указана: `python main.py`.

Для постоянного хранения SQLite подключите Railway Volume к `/data`. Без Volume база может исчезнуть после пересоздания контейнера.

## 8. Сервер/VPS и перезапуск

После загрузки проекта установите зависимости, создайте `.env` и запустите `python main.py`. Для постоянной работы используйте systemd, Docker, Supervisor или tmux.

При systemd:

```bash
sudo systemctl restart whisper-team-bot
sudo systemctl status whisper-team-bot
```

## 9. Защита `.env`

`.env` и `bot.db` уже добавлены в `.gitignore`. Не загружайте их на GitHub, не отправляйте скриншоты токена и храните секреты Railway только в разделе Variables.

## 10. База данных

Автоматически создаются таблицы `users`, `applications`, `support_tickets`, `messages`, `admin_actions`, `blocked_users`. Данные и незакрытые обращения сохраняются после перезапуска, пока файл базы не удалён.
