"""Построители inline-клавиатур."""

import calendar
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_USERNAME

# Русские названия месяцев и дней недели
MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}
DAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📅 Записаться", callback_data="booking_start")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отменить запись", callback_data="cancel_booking")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Прайс", callback_data="prices"),
        InlineKeyboardButton(text="📸 Портфолио", callback_data="portfolio")
    )
    # Ссылка на контакт админа
    contact_url = f"https://t.me/{ADMIN_USERNAME.lstrip('@')}"
    builder.row(
        InlineKeyboardButton(text="💬 Написать мне по вопросам", url=contact_url)
    )
    return builder.as_markup()


def calendar_kb(year: int, month: int, available_dates: list[str]) -> InlineKeyboardMarkup:
    """Inline-календарь с навигацией по месяцам."""
    builder = InlineKeyboardBuilder()

    # Заголовок: < Март 2026 >
    builder.row(
        InlineKeyboardButton(text="◀️", callback_data=f"cal_prev_{year}_{month}"),
        InlineKeyboardButton(
            text=f"{MONTHS_RU[month]} {year}",
            callback_data="cal_ignore"
        ),
        InlineKeyboardButton(text="▶️", callback_data=f"cal_next_{year}_{month}")
    )

    # Дни недели
    day_buttons = [
        InlineKeyboardButton(text=day, callback_data="cal_ignore")
        for day in DAYS_RU
    ]
    builder.row(*day_buttons)

    # Дни месяца
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        week_buttons = []
        for day in week:
            if day == 0:
                week_buttons.append(
                    InlineKeyboardButton(text=" ", callback_data="cal_ignore")
                )
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                if date_str in available_dates:
                    # Доступная дата — активная кнопка
                    week_buttons.append(
                        InlineKeyboardButton(
                            text=f"✅ {day}",
                            callback_data=f"cal_day_{date_str}"
                        )
                    )
                else:
                    # Недоступная дата — неактивная
                    week_buttons.append(
                        InlineKeyboardButton(
                            text=str(day),
                            callback_data="cal_ignore"
                        )
                    )
        builder.row(*week_buttons)

    # Кнопка назад
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    )
    return builder.as_markup()


def time_slots_kb(slots: list[dict], date: str) -> InlineKeyboardMarkup:
    """Кнопки с доступным временем на выбранную дату."""
    builder = InlineKeyboardBuilder()
    for slot in slots:
        builder.button(
            text=f"🕐 {slot['time']}",
            callback_data=f"slot_{slot['id']}"
        )
    # Располагаем по 3 в ряд
    builder.adjust(3)

    # Кнопка назад к календарю
    builder.row(
        InlineKeyboardButton(text="🔙 К календарю", callback_data="booking_start")
    )
    return builder.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    """Подтверждение / отмена записи."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_no")
    )
    return builder.as_markup()


def cancel_confirm_kb(booking_id: int) -> InlineKeyboardMarkup:
    """Подтверждение отмены записи."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, отменить",
            callback_data=f"cancel_yes_{booking_id}"
        ),
        InlineKeyboardButton(text="❌ Нет", callback_data="back_to_menu")
    )
    return builder.as_markup()


def subscription_kb(channel_link: str) -> InlineKeyboardMarkup:
    """Кнопки подписки на канал."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📢 Подписаться", url=channel_link)
    )
    builder.row(
        InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription")
    )
    return builder.as_markup()


# ── Клавиатуры администратора ──


def admin_menu_kb() -> InlineKeyboardMarkup:
    """Меню админ-панели."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📅 Добавить рабочий день", callback_data="admin_add_day")
    )
    builder.row(
        InlineKeyboardButton(text="🕐 Добавить слот", callback_data="admin_add_slot"),
        InlineKeyboardButton(text="🗑 Удалить слот", callback_data="admin_delete_slot")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отменить запись клиента", callback_data="admin_cancel_booking")
    )
    builder.row(
        InlineKeyboardButton(text="🔒 Закрыть день", callback_data="admin_close_day")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Просмотр расписания", callback_data="admin_view_schedule")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Редактировать прайсы", callback_data="admin_edit_prices"),
        InlineKeyboardButton(text="🏠 Изменить адрес", callback_data="admin_edit_address")
    )
    builder.row(
        InlineKeyboardButton(text="🖼 Управление портфолио", callback_data="admin_portfolio")
    )
    return builder.as_markup()


def admin_dates_kb(dates: list[str], action: str) -> InlineKeyboardMarkup:
    """Список дат для выбора в админ-панели."""
    builder = InlineKeyboardBuilder()
    for date in dates:
        builder.button(
            text=f"📅 {date}",
            callback_data=f"{action}_{date}"
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")
    )
    return builder.as_markup()


def admin_slots_kb(slots: list[dict], action: str) -> InlineKeyboardMarkup:
    """Список слотов для выбора (удаление, отмена записи)."""
    builder = InlineKeyboardBuilder()
    for slot in slots:
        label = slot.get("time", "")
        if slot.get("name"):
            label += f" — {slot['name']}"
        cb_id = slot.get("slot_id", slot.get("id"))
        builder.button(text=label, callback_data=f"{action}_{cb_id}")
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")
    )
    return builder.as_markup()


def admin_services_kb(services: list[dict]) -> InlineKeyboardMarkup:
    """Список услуг для редактирования (админ)."""
    builder = InlineKeyboardBuilder()
    for svc in services:
        builder.button(
            text=f"✏️ {svc['name']} — {svc['price']}₽",
            callback_data=f"svc_edit_{svc['id']}"
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="➕ Добавить услугу", callback_data="svc_add"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")
    )
    return builder.as_markup()


def service_edit_actions_kb(service_id: int) -> InlineKeyboardMarkup:
    """Действия над услугой."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏷 Изменить цену", callback_data=f"svc_price_{service_id}"),
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"svc_del_{service_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 К списку", callback_data="admin_edit_prices")
    )
    return builder.as_markup()


def user_services_kb(services: list[dict]) -> InlineKeyboardMarkup:
    """Список услуг для выбора пользователем при бронировании."""
    builder = InlineKeyboardBuilder()
    for svc in services:
        builder.button(
            text=f"{svc['name']} — {svc['price']}₽",
            callback_data=f"select_svc_{svc['id']}"
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="🤷‍♀️ Не знаю / Обсудим на месте", callback_data="select_svc_dont_know")
    )
    return builder.as_markup()
def portfolio_gallery_kb(photo_index: int, total_photos: int, is_admin: bool = False, photo_id: int | None = None) -> InlineKeyboardMarkup:
    """Клавиатура для навигации по портфолио."""
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    nav_row = []
    if photo_index > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"port_prev_{photo_index}"))
    
    nav_row.append(InlineKeyboardButton(text=f"{photo_index + 1}/{total_photos}", callback_data="ignore"))
    
    if photo_index < total_photos - 1:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"port_next_{photo_index}"))
    
    builder.row(*nav_row)
    
    # Кнопка удаления для админа
    if is_admin and photo_id is not None:
        builder.row(InlineKeyboardButton(text="🗑 Удалить фото", callback_data=f"port_del_{photo_id}"))
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    
    return builder.as_markup()


def admin_portfolio_kb() -> InlineKeyboardMarkup:
    """Клавиатура управления портфолио для админа."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Добавить фото", callback_data="admin_port_add"))
    builder.row(InlineKeyboardButton(text="🖼 Просмотр/Удаление", callback_data="admin_port_view"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu"))
    return builder.as_markup()
