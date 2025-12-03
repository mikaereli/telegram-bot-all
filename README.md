# Telegram Bot для упоминания участников группы

Этот бот позволяет сохранять список участников группы и упоминать их всех одной командой, даже если у них отключены уведомления.

## Функционал
- `/all` - отметить всех участников

## Структура проекта

```
telegram_bot/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── main.py
└── src/
    ├── __init__.py
    ├── bot.py
    ├── config.py
    ├── database.py
└── db/
    ├── bot_database.db
```

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/mikaereli/telegram-bot-all.git
cd telegram-bot-all
```

2. Создайте виртуальное окружение и активируйте его:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории проекта:
```
BOT_TOKEN=your_bot_token_here
```

## Настройка бота

1. Получите токен бота у [@BotFather](https://t.me/BotFather)
2. Вставьте полученный токен в файл `.env`
3. Запустите бота:
```bash
python main.py
```

## База данных

Бот использует SQLite для хранения информации о группах и участниках. База данных создается автоматически при первом запуске в директории `src/db/`.

Структура базы данных:
- Таблица `groups`: хранит информацию о группах
  - `group_id` (PRIMARY KEY)
  - `name`
- Таблица `members`: хранит информацию об участниках
  - `id` (PRIMARY KEY)
  - `username`
  - `group_id` (FOREIGN KEY)

