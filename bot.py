import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8736143167:AAE_v_fdmk0TlF6HfGaZjCrtdLgIjOC42vQ"
ADMIN_ID = 1043945034

# === ВАШ РАБОЧИЙ ПРОКСИ ===
PROXY_URL = "socks5://yP7CeJ:ZeBeFBEY8Uv8@bproxy.site:16185"
# ===========================

# Настройка прокси для сессии
session = requests.Session()
session.proxies = {
    'http': PROXY_URL,
    'https': PROXY_URL
}

# Передаём прокси в бота
bot = telebot.TeleBot(BOT_TOKEN, request=session)

# ------------------- МЕНЮ С КНОПКАМИ -------------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📅 Забронировать смену", callback_data="book"),
        InlineKeyboardButton("📋 Мои заявки", callback_data="my_requests"),
        InlineKeyboardButton("📞 Поддержка", callback_data="support"),
        InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
    )
    bot.send_message(
        message.chat.id,
        "✨ *Добро пожаловать!* ✨\n\n"
        "Я помогу тебе быстро забронировать рабочую смену.\n\n"
        "👇 *Выбери действие:* 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ------------------- ОБРАБОТЧИК КНОПОК -------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    bot.answer_callback_query(call.id)

    if call.data == "book":
        bot.edit_message_text(
            "📅 *Функция бронирования*\n\nСкоро здесь появится выбор даты и времени.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        bot.send_message(ADMIN_ID, f"Пользователь {call.from_user.first_name} начал бронирование.")

    elif call.data == "my_requests":
        bot.edit_message_text(
            "📋 *Ваши заявки*\n\nУ вас пока нет активных заявок.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    elif call.data == "support":
        bot.edit_message_text(
            "📞 *Поддержка*\n\nПо всем вопросам обращайтесь к администратору.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    elif call.data == "help":
        bot.edit_message_text(
            "ℹ️ *Помощь*\n\nПросто нажмите «Создать заявку» и следуйте инструкциям.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

# ------------------- ЗАПУСК -------------------
print("Бот запущен с SOCKS5 прокси...")
bot.infinity_polling()
