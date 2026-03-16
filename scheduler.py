"""APScheduler — автонапоминания за 24 часа до записи."""

from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import get_all_future_bookings

# Глобальный планировщик
scheduler = AsyncIOScheduler(timezone="Asia/Yekaterinburg")


async def send_reminder(bot, user_id: int, time_str: str):
    """Отправить напоминание клиенту."""
    try:
        await bot.send_message(
            user_id,
            f"💅 <b>Напоминание!</b>\n\n"
            f"Напоминаем, что вы записаны на маникюр завтра в <b>{time_str}</b>.\n"
            f"Ждём вас! ❤️",
            parse_mode="HTML"
        )
    except Exception as e:
        # Пользователь мог заблокировать бота
        print(f"Не удалось отправить напоминание user_id={user_id}: {e}")


def schedule_reminder(bot, booking_id: int, user_id: int, appointment_dt: datetime):
    """
    Запланировать напоминание за 24 часа до визита.
    Если до визита менее 24 часов — не создаём напоминание.
    """
    reminder_time = appointment_dt - timedelta(hours=24)
    now = datetime.now()

    if reminder_time <= now:
        # Менее 24 часов до визита — напоминание не нужно
        return

    job_id = f"reminder_{booking_id}"
    scheduler.add_job(
        send_reminder,
        "date",
        run_date=reminder_time,
        args=[bot, user_id, appointment_dt.strftime("%H:%M")],
        id=job_id,
        replace_existing=True
    )


def remove_reminder(booking_id: int):
    """Удалить задачу напоминания при отмене записи."""
    job_id = f"reminder_{booking_id}"
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass  # Задача могла уже выполниться или не существовать


async def restore_reminders(bot):
    """Восстановить все напоминания из БД при перезапуске бота."""
    bookings = await get_all_future_bookings()
    count = 0
    for booking in bookings:
        appointment_dt = datetime.strptime(
            f"{booking['date']} {booking['time']}", "%Y-%m-%d %H:%M"
        )
        reminder_time = appointment_dt - timedelta(hours=24)
        if reminder_time > datetime.now():
            schedule_reminder(bot, booking["booking_id"], booking["user_id"], appointment_dt)
            count += 1
    print(f"Восстановлено {count} напоминаний")
