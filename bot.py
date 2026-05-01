import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8736143167:AAE_v_fdmk0TlF6HfGaZjCrtdLgIjOC42vQ"
ADMIN_ID = 1043945034

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("📅 Забронировать смену")
    btn2 = KeyboardButton("📋 Мои заявки")
    btn3 = KeyboardButton("📞 Поддержка")
    btn4 = KeyboardButton("ℹ️ Помощь")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "✨ Добро пожаловать! ✨\n\n👇 Выбери действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "📅 Забронировать смену":
        bot.send_message(message.chat.id, "📅 Функция бронирования скоро появится!")
        bot.send_message(ADMIN_ID, f"Пользователь {message.from_user.first_name} хочет смену")
    elif message.text == "📋 Мои заявки":
        bot.send_message(message.chat.id, "📋 У вас пока нет активных заявок.")
    elif message.text == "📞 Поддержка":
        bot.send_message(message.chat.id, "📞 По вопросам пишите администратору.")
    elif message.text == "ℹ️ Помощь":
        bot.send_message(message.chat.id, "ℹ️ Нажмите «Забронировать смену».")
    else:
        bot.send_message(message.chat.id, "❌ Используйте кнопки меню.")

print("✅ Бот запущен!")
bot.infinity_polling()
