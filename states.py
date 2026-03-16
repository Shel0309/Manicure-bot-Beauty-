"""FSM-состояния для бота."""

from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    """Состояния процесса записи клиента."""
    waiting_name = State()       # Ожидание ввода имени
    waiting_phone = State()      # Ожидание ввода телефона
    waiting_service = State()    # Ожидание выбора/ввода услуги
    confirm_booking = State()    # Подтверждение записи


class AdminStates(StatesGroup):
    """Состояния админ-панели."""
    add_day_date = State()           # Ввод даты для добавления рабочего дня
    add_slot_date = State()          # Выбор даты для добавления слота
    add_slot_time = State()          # Ввод времени нового слота
    delete_slot_select = State()     # Выбор слота для удаления
    cancel_booking_select = State()  # Выбор записи для отмены
    close_day_date = State()         # Выбор даты для закрытия дня
    view_schedule_date = State()     # Выбор даты для просмотра расписания
    
    # Редактирование прайсов
    edit_services_list = State()      # Просмотр списка услуг
    add_service_name = State()        # Ввод названия услуги
    add_service_price = State()       # Ввод цены услуги
    edit_service_select = State()     # Выбор услуги для редактирования
    edit_service_price = State()      # Ввод новой цены услуги

    # Редактирование адреса
    edit_address = State()

    # Управление портфолио
    manage_portfolio = State()
    add_portfolio_photo = State()
