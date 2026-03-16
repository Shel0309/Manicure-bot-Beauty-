# 💅 Telegram-бот для мастера маникюра

Бот для онлайн-записи к мастеру маникюра с админ-панелью, проверкой подписки на канал и автонапоминаниями.

## 📋 Возможности

**Для клиентов:**
- 📅 Запись через inline-календарь
- ❌ Отмена записи
- 💰 Просмотр прайс-листа
- 📸 Портфолио (ссылка на Pinterest)
- 🔔 Автонапоминание за 24 часа до визита

**Для администратора:**
- 📅 Добавление рабочих дней
- 🕐 Добавление / удаление слотов
- ❌ Отмена записей клиентов
- 🔒 Закрытие дня
- 📋 Просмотр расписания

## 🗂 Структура проекта

```
├── bot.py              # Точка входа
├── config.py           # Конфигурация (.env)
├── database.py         # SQLite — слоты и записи
├── keyboards.py        # Inline-клавиатуры
├── states.py           # FSM-состояния
├── scheduler.py        # APScheduler — напоминания
├── handlers/
│   ├── __init__.py
│   ├── start.py        # /start + проверка подписки
│   ├── booking.py      # Запись (календарь → время → имя → телефон)
│   ├── cancel.py       # Отмена записи
│   ├── prices.py       # Прайс-лист
│   ├── portfolio.py    # Портфолио
│   └── admin.py        # Админ-панель
├── .env.example        # Шаблон переменных окружения
├── requirements.txt    # Зависимости
└── README.md
```

## 🚀 Быстрый запуск (локально, без Docker)

### 1. Клонируйте / скопируйте проект

```bash
cd путь/к/проекту
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv
```

Активация:
- **Windows:** `venv\Scripts\activate`
- **Linux/macOS:** `source venv/bin/activate`

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

Скопируйте файл-шаблон и заполните своими данными:

```bash
copy .env.example .env
```

Откройте `.env` и укажите:

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен бота от [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | Ваш Telegram ID (узнать: [@userinfobot](https://t.me/userinfobot)) |
| `CHANNEL_ID` | ID или @username канала для проверки подписки |
| `CHANNEL_LINK` | Ссылка на канал (https://t.me/...) |
| `SCHEDULE_CHANNEL_ID` | ID или @username канала для публикации расписания |

> ⚠️ **Важно:** Бот должен быть администратором в обоих каналах!

### 5. Запустите бота

```bash
python bot.py
```

## 🐳 Запуск в Docker

### Вариант A: Локальный запуск в Docker

1. **Убедитесь, что установлены Docker и Docker Compose.**

2. **Создайте `.env` (или отредактируйте существующий):**

```bash
cp .env.example .env    # Linux/macOS
REM copy .env.example .env  # Windows (PowerShell/CMD)
```

Заполните переменные `BOT_TOKEN`, `ADMIN_ID`, `CHANNEL_ID`, `CHANNEL_LINK`, `SCHEDULE_CHANNEL_ID`.

3. **Соберите и запустите контейнер:**

```bash
docker compose up -d --build
```

4. **Остановить контейнер:**

```bash
docker compose down
```

### Вариант B: Установка на сервер Ubuntu (через Docker)

Ниже — полный пошаговый гайд для чистого сервера Ubuntu 20.04/22.04+.

#### 1. Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Установка Docker

```bash
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Добавьте текущего пользователя в группу `docker` (чтобы не писать `sudo` каждый раз):

```bash
sudo usermod -aG docker $USER
```

> После этого перелогиньтесь (выйдите и зайдите в сессию SSH), чтобы группа применилась.

#### 3. Клонирование / загрузка проекта на сервер

Вариант через `git`:

```bash
cd ~
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> manicure-bot
cd manicure-bot
```

Или загрузите файлы проекта по SFTP/FTP и поместите их, например, в `~/manicure-bot`.

#### 4. Создание файла `.env` на сервере

```bash
cd ~/manicure-bot
cp .env.example .env
nano .env
```

Укажите реальные значения:

- `BOT_TOKEN` — токен от `@BotFather`
- `ADMIN_ID` — ваш Telegram ID
- `CHANNEL_ID` — канал для проверки подписки
- `CHANNEL_LINK` — ссылка на канал
- `SCHEDULE_CHANNEL_ID` — канал для расписания

Сохраните файл (`Ctrl+O`, `Enter`, `Ctrl+X`).

#### 5. Первый запуск бота в Docker

```bash
cd ~/manicure-bot
docker compose up -d --build
```

Проверка логов:

```bash
docker compose logs -f
```

Остановить:

```bash
docker compose down
```

#### 6. Автостарт бота при перезагрузке сервера

Docker Compose уже запускает контейнер с политикой `restart: unless-stopped`, поэтому при перезагрузке Docker сам поднимет контейнер. Достаточно один раз запустить:

```bash
cd ~/manicure-bot
docker compose up -d --build
```

Если хотите, можно обернуть это в `systemd`-сервис, но в большинстве случаев это не требуется.

## 🖥 Запуск на локальном сервере (VPS / PC) без Docker

### Вариант 1: Через `systemd` (Linux)

Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/manicure-bot.service
```

Содержимое:

```ini
[Unit]
Description=Manicure Telegram Bot
After=network.target

[Service]
Type=simple
User=ваш_пользователь
WorkingDirectory=/путь/к/проекту
ExecStart=/путь/к/проекту/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск:

```bash
sudo systemctl daemon-reload
sudo systemctl enable manicure-bot
sudo systemctl start manicure-bot
```

Проверка статуса:

```bash
sudo systemctl status manicure-bot
```

### Вариант 2: Через `screen` (быстро, без systemd)

```bash
screen -S manicure-bot
cd /путь/к/проекту
source venv/bin/activate
python bot.py
```

Отключиться от сессии: `Ctrl+A`, затем `D`

Вернуться: `screen -r manicure-bot`

### Вариант 3: Windows — через bat-файл

Создайте `start_bot.bat`:

```bat
@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python bot.py
pause
```

Дважды кликните для запуска. Для автозапуска — добавьте ярлык в папку `Автозагрузка` (`shell:startup`).

## 📱 Первые шаги после запуска

1. Отправьте боту `/start` — появится главное меню
2. Отправьте `/admin` (от аккаунта с `ADMIN_ID`) — откроется админ-панель
3. Добавьте рабочие дни и слоты через админ-панель
4. Готово! Клиенты могут записываться

## ⚙️ Технологии

- **Python 3.10+**
- **aiogram 3.15** — асинхронный фреймворк для Telegram Bot API
- **aiosqlite** — асинхронный SQLite
- **APScheduler** — планировщик задач (напоминания)
- **python-dotenv** — загрузка `.env`
