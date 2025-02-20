from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from datetime import datetime, timedelta

# Меню ресторана
menu = {
    "Закуски": ["Сырная тарелка - 800 руб.", "Брускетта с томатами - 450 руб."],
    "Основные блюда": ["Стейк из говядины - 1500 руб.", "Паста Карбонара - 900 руб."],
    "Десерты": ["Тирамису - 600 руб.", "Чизкейк - 550 руб."],
    "Напитки": ["Мохито - 400 руб.", "Вино Merlot - 1200 руб./бокал"],
}

# Состояние пользователя
user_state = {}


# Функция создания списка времени с 10:00 до 20:00 (каждые 30 минут)
def get_time_slots():
    return [f"{hour:02d}:{minute:02d}" for hour in range(10, 20) for minute in (0, 30)]


# Функция создания списка дат на месяц вперед
def get_available_dates():
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(30)]


# Команда /start
async def start(update: Update, context: CallbackContext):
    buttons = [
        ["🍽 Забронировать столик"],
        ["📜 Меню"],
        ["🏠 О нас"],
        ["🛎 Вызвать персонал"],
    ]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать в Gourmet Haven!", reply_markup=keyboard
    )


# Обработка выбора "Забронировать столик"
async def book_table(update: Update, context: CallbackContext):
    user_state[update.message.chat_id] = {}  # Очищаем состояние пользователя
    buttons = [["Сегодня"], ["Завтра"], ["Другой день"], ["🔙 Назад"]]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Выберите дату:", reply_markup=keyboard)


# Обработка выбора даты
async def choose_date(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    if text == "Сегодня":
        user_state[chat_id]["date"] = datetime.today().strftime("%d.%m.%Y")
    elif text == "Завтра":
        user_state[chat_id]["date"] = (datetime.today() + timedelta(days=1)).strftime(
            "%d.%m.%Y"
        )
    elif text == "Другой день":
        buttons = [[date] for date in get_available_dates()[:7]] + [["🔙 Назад"]]
        keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        await update.message.reply_text("Выберите дату:", reply_markup=keyboard)
        return

    buttons = [[time] for time in get_time_slots()] + [["🔙 Назад"]]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Выберите время:", reply_markup=keyboard)


# Обработка выбора времени
async def choose_time(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    time = update.message.text

    if time == "🔙 Назад":
        await book_table(update, context)
        return

    if time not in get_time_slots():
        await update.message.reply_text("Выберите корректное время!")
        return

    user_state[chat_id]["time"] = time
    date = user_state[chat_id]["date"]

    await update.message.reply_text(
        f"✅ Ваш столик забронирован на *{date}* в *{time}*.\n"
        "Ожидайте звонка от нашего менеджера для подтверждения брони. "
        "Спасибо, что выбрали *Gourmet Haven*!",
        parse_mode="Markdown",
    )


# Обработка текстовых сообщений
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat_id

    if text == "📜 Меню":
        for category, items in menu.items():
            await update.message.reply_text(f"{category}:\n" + "\n".join(items))
    elif text == "🏠 О нас":
        await update.message.reply_text(
            "Добро пожаловать в ресторан Gourmet Haven!\nАдрес: ул. Главная, 15\nТелефон: +7 (XXX) XXX-XX-XX"
        )
    elif text == "🛎 Вызвать персонал":
        await update.message.reply_text("Сейчас позовем персонал!")
    elif text == "🍽 Забронировать столик":
        await book_table(update, context)
    elif text in ["Сегодня", "Завтра", "Другой день"]:
        await choose_date(update, context)
    elif text in get_time_slots():
        await choose_time(update, context)
    elif text in get_available_dates():
        user_state[chat_id]["date"] = text
        buttons = [[time] for time in get_time_slots()] + [["🔙 Назад"]]
        keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        await update.message.reply_text("Выберите время:", reply_markup=keyboard)
    elif text == "🔙 Назад":
        await start(update, context)


# Запуск бота
app = (
    Application.builder()
    .token("7338617614:AAExMLzMaFRW-rlHFc3FG8o2dWtReEm-7S8")
    .build()
)

# Добавляем обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запуск бота
app.run_polling()
