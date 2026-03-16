"""Слой базы данных — SQLite операции для слотов и записей."""

import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")


async def init_db():
    """Создание таблиц при первом запуске."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                is_booked INTEGER DEFAULT 0,
                is_closed INTEGER DEFAULT 0,
                UNIQUE(date, time)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price INTEGER NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                slot_id INTEGER NOT NULL,
                service TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (slot_id) REFERENCES slots(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL
            )
        """)
        # Инициализируем адрес по умолчанию, если его нет
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('address', 'Адрес не указан')")
        await db.commit()


async def add_slot(date: str, time: str):
    """Добавить временной слот на указанную дату."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO slots (date, time) VALUES (?, ?)",
                (date, time)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            # Слот уже существует
            return False


async def add_work_day(date: str, default_times: list[str] = None):
    """Добавить рабочий день с набором стандартных слотов."""
    if default_times is None:
        default_times = [
            "09:00", "10:00", "11:00", "12:00",
            "13:00", "14:00", "15:00", "16:00",
            "17:00", "18:00"
        ]
    added = 0
    for time in default_times:
        if await add_slot(date, time):
            added += 1
    return added


async def get_available_dates() -> list[str]:
    """Получить список дат, на которых есть свободные слоты."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT DISTINCT date FROM slots
            WHERE is_booked = 0 AND is_closed = 0
              AND date >= date('now', 'localtime')
            ORDER BY date
        """)
        rows = await cursor.fetchall()
        return [row["date"] for row in rows]


async def get_available_times(date: str) -> list[dict]:
    """Получить доступные слоты на конкретную дату."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT id, time FROM slots
            WHERE date = ? AND is_booked = 0 AND is_closed = 0
            ORDER BY time
        """, (date,))
        rows = await cursor.fetchall()
        return [{"id": row["id"], "time": row["time"]} for row in rows]


async def get_slot_by_id(slot_id: int) -> dict | None:
    """Получить информацию о слоте по ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM slots WHERE id = ?", (slot_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def book_slot(user_id: int, username: str | None, slot_id: int, service: str, name: str, phone: str) -> bool:
    """Забронировать слот. Возвращает False если слот уже занят."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем, свободен ли слот
        cursor = await db.execute(
            "SELECT is_booked, is_closed FROM slots WHERE id = ?", (slot_id,)
        )
        row = await cursor.fetchone()
        if not row or row[0] == 1 or row[1] == 1:
            return False

        # Помечаем слот как забронированный
        await db.execute(
            "UPDATE slots SET is_booked = 1 WHERE id = ?", (slot_id,)
        )
        # Создаём запись
        await db.execute(
            "INSERT INTO bookings (user_id, username, slot_id, service, name, phone) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, slot_id, service, name, phone)
        )
        await db.commit()
        return True


async def get_user_booking(user_id: int) -> dict | None:
    """Получить активную запись пользователя (одна на пользователя)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT b.id, b.name, b.phone, b.slot_id,
                   s.date, s.time
            FROM bookings b
            JOIN slots s ON b.slot_id = s.id
            WHERE b.user_id = ?
              AND s.date >= date('now', 'localtime')
            ORDER BY s.date, s.time
            LIMIT 1
        """, (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def cancel_booking(booking_id: int) -> dict | None:
    """Отменить запись — освободить слот и удалить бронь. Возвращает данные записи."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Получаем данные записи перед удалением
        cursor = await db.execute("""
            SELECT b.*, s.date, s.time
            FROM bookings b JOIN slots s ON b.slot_id = s.id
            WHERE b.id = ?
        """, (booking_id,))
        booking = await cursor.fetchone()
        if not booking:
            return None

        booking_data = dict(booking)

        # Освобождаем слот
        await db.execute(
            "UPDATE slots SET is_booked = 0 WHERE id = ?",
            (booking_data["slot_id"],)
        )
        # Удаляем запись
        await db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        await db.commit()
        return booking_data


async def cancel_booking_by_slot(slot_id: int) -> dict | None:
    """Отменить запись по ID слота (для админа)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id FROM bookings WHERE slot_id = ?", (slot_id,)
        )
        row = await cursor.fetchone()
        if row:
            return await cancel_booking(row["id"])
        return None


async def close_day(date: str) -> int:
    """Закрыть день — пометить все слоты как закрытые. Возвращает количество закрытых."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE slots SET is_closed = 1 WHERE date = ? AND is_booked = 0",
            (date,)
        )
        await db.commit()
        return cursor.rowcount


async def get_day_schedule(date: str) -> list[dict]:
    """Получить полное расписание на день (все слоты)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT s.id, s.time, s.is_booked, s.is_closed,
                   b.name, b.phone, b.user_id
            FROM slots s
            LEFT JOIN bookings b ON s.id = b.slot_id
            WHERE s.date = ?
            ORDER BY s.time
        """, (date,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_slot(slot_id: int) -> bool:
    """Удалить слот (только свободный, не забронированный)."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM slots WHERE id = ? AND is_booked = 0",
            (slot_id,)
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_all_future_bookings() -> list[dict]:
    """Получить все будущие записи (для восстановления напоминаний)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT b.id AS booking_id, b.user_id, b.name,
                   s.date, s.time
            FROM bookings b
            JOIN slots s ON b.slot_id = s.id
            WHERE s.date >= date('now', 'localtime')
            ORDER BY s.date, s.time
        """)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_dates_with_slots() -> list[str]:
    """Получить все даты, на которых есть хотя бы один слот (для админа)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT DISTINCT date FROM slots
            WHERE date >= date('now', 'localtime')
            ORDER BY date
        """)
        rows = await cursor.fetchall()
        return [row["date"] for row in rows]


async def get_booked_slots_for_date(date: str) -> list[dict]:
    """Получить забронированные слоты на дату (для отмены админом)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT s.id AS slot_id, s.time, b.id AS booking_id,
                   b.name, b.phone, b.user_id, b.username, b.service
            FROM slots s
            JOIN bookings b ON s.id = b.slot_id
            WHERE s.date = ?
            ORDER BY s.time
        """, (date,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# ── Функции для работы с услугами (прайсами) ──


async def get_all_services() -> list[dict]:
    """Получить список всех услуг."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM services ORDER BY name")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def add_service(name: str, price: int) -> bool:
    """Добавить новую услугу."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO services (name, price) VALUES (?, ?)",
                (name, price)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def update_service(service_id: int, name: str, price: int) -> bool:
    """Обновить данные услуги."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE services SET name = ?, price = ? WHERE id = ?",
            (name, price, service_id)
        )
        await db.commit()
        return True


async def delete_service(service_id: int) -> bool:
    """Удалить услугу."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM services WHERE id = ?", (service_id,))
        await db.commit()
        return True


async def get_service_by_id(service_id: int) -> dict | None:
    """Получить услугу по ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
async def get_setting(key: str) -> str | None:
    """Получить значение настройки по ключу."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row["value"] if row else None


async def update_setting(key: str, value: str):
    """Обновить или добавить настройку."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        await db.commit()


async def add_portfolio_photo(file_id: str):
    """Добавить фото в портфолио."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO portfolio (file_id) VALUES (?)", (file_id,))
        await db.commit()


async def get_portfolio_photos():
    """Получить все фото из портфолио."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, file_id FROM portfolio ORDER BY id DESC") as cursor:
            rows = await cursor.fetchall()
            return [{"id": row[0], "file_id": row[1]} for row in rows]


async def delete_portfolio_photo(photo_id: int):
    """Удалить фото из портфолио."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM portfolio WHERE id = ?", (photo_id,))
        await db.commit()
