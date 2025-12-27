import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота из переменных окружений
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка токена
if not BOT_TOKEN:
    raise ValueError("⚠️ ОШИБКА: BOT_TOKEN не найден! Создайте .env файл с BOT_TOKEN=ваш_токен")

# Другие настройки
DATABASE_NAME = "casino.db"
START_BALANCE = 1000

# Проверка, что токен действителен (базовая проверка)
if not BOT_TOKEN.startswith(("5", "6")):
    raise ValueError("⚠️ ОШИБКА: Неверный формат токена бота!")
