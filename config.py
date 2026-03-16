"""Конфигурация бота — загрузка переменных окружения."""

import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram ID администратора (владелец бота)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Канал, на который нужно подписаться для записи
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Например: "@my_channel" или "-100123456789"
CHANNEL_LINK = os.getenv("CHANNEL_LINK")  # Ссылка: https://t.me/my_channel

# Канал для публикации расписания
SCHEDULE_CHANNEL_ID = os.getenv("SCHEDULE_CHANNEL_ID")  # ID или @username канала

# Юзернейм админа для связи (без @)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "t.me/placeholder")
