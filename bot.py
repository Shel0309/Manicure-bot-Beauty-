"""Точка входа — инициализация бота, подключение роутеров, запуск."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from scheduler import scheduler, restore_reminders

# Импорт роутеров
from handlers import start, booking, cancel, prices, portfolio, admin


async def on_startup(bot: Bot):
    """Действия при запуске бота."""
    # Инициализация базы данных
    await init_db()
    logging.info("База данных инициализирована")

    # Восстановление напоминаний из БД
    await restore_reminders(bot)

    # Запуск планировщика
    scheduler.start()
    logging.info("Планировщик запущен")


async def main():
    """Основная функция запуска бота."""
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все роутеры
    dp.include_routers(
        start.router,
        booking.router,
        cancel.router,
        prices.router,
        portfolio.router,
        admin.router,
    )

    # Регистрируем startup-хук
    dp.startup.register(on_startup)

    logging.info("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    asyncio.run(main())
