import os
import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
)

from datetime import datetime, timedelta
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = os.getenv("PORT")

if not TOKEN:
    raise ValueError("Не найден TOKEN. Укажите его в переменных окружения.")
if not PORT:
    raise ValueError("Не найден PORT. Укажите его в переменных окружения.")
PORT = int(PORT)

# Создаем Flask-приложение
app = Flask(__name__)

# Меню ресторана
menu = {
    "Закуски": ["Сырная тарелка - 800 руб.", "Брускетта с томатами - 450 руб."],
    "Основные блюда": ["Стейк из говядины - 1500 руб.", "Паста Карбонара - 900 руб."],
    "Десерты": ["Тирамису - 600 руб.", "Чизкейк - 550 руб."],
    "Напитки": ["Мохито - 400 руб.", "Вино Merlot - 1200 руб./бокал"],
}

# Функция создания списка времени с 10:00 до 20:00 (каждые 30 минут)
def get_time_slots():
    return [f"{hour:02d}:{minute:02d}" for hour in range(10, 20) for minute in (0, 30)]

# Функция создания списка дат на месяц вперед
def get_available_dates():
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(30)]

# Инициализация Telegram-бота
bot_app = Application.builder().token(TOKEN).updater(None).build()

# Команда /start
async def start(update: Update, context: CallbackContext):
    buttons = [["🍽 Забронировать столик"], ["📜 Меню"], ["🏠 О нас"], ["🛎 Вызвать персонал"]]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать в Gourmet Haven!", reply_markup=keyboard)

# Обработка текстовых сообщений
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "📜 Меню":
        for category, items in menu.items():
            await update.message.reply_text(f"{category}:\n" + "\n".join(items))
    elif text == "🏠 О нас":
        await update.message.reply_text("Добро пожаловать в ресторан Gourmet Haven!\nАдрес: ул. Главная, 15\nТелефон: +7 (XXX) XXX-XX-XX")
    elif text == "🛎 Вызвать персонал":
        await update.message.reply_text("Сейчас позовем персонал!")
    elif text == "🍽 Забронировать столик":
        await update.message.reply_text("Бронирование пока недоступно.")

# Добавляем обработчики команд
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Маршрут для проверки работы
@app.route("/", methods=["GET"])
def home():
    logger.info("Обработка запроса по корневому пути")
    return "Bot is running!", 200

# Обработчик Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
async def handle_webhook():
    logger.info("Обработка запроса от Telegram")
    try:
        update = Update.de_json(request.get_json(), bot_app.bot)
        await bot_app.process_update(update)
        return "", 200
    except Exception as e:
        logger.error(f"Ошибка обработки Webhook: {e}")
        return "", 500

# Устанавливаем Webhook
async def set_webhook():
    await bot_app.initialize()
    await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

if __name__ == "__main__":
    asyncio.run(set_webhook())  # Устанавливаем Webhook
    app.run(host="0.0.0.0", port=PORT)
