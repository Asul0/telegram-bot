import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN or not WEBHOOK_URL:
    raise ValueError("Не найден TOKEN или WEBHOOK_URL!")

# Создание Flask
app = Flask(__name__)

# Telegram Bot
bot_app = (
    Application.builder()
    .token(TOKEN)
    .updater(None)
    .build()
)

# Команда /start
async def start(update: Update, context: CallbackContext):
    buttons = [["🍽 Забронировать столик"], ["📜 Меню"], ["🏠 О нас"], ["🛎 Вызвать персонал"]]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать в Gourmet Haven!", reply_markup=keyboard)

bot_app.add_handler(CommandHandler("start", start))

# Главная страница
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

# Webhook обработчик
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    try:
        update = Update.de_json(request.get_json(), bot_app.bot)
        asyncio.run(bot_app.process_update(update))
        return "", 200
    except Exception as e:
        logger.error(f"Ошибка обработки Webhook: {e}")
        return "", 500

# Устанавливаем Webhook перед запуском
@app.before_first_request
def setup_webhook():
    asyncio.run(set_webhook())

async def set_webhook():
    await bot_app.initialize()
    await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

# Запуск Flask
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
