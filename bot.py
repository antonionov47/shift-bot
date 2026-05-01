import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8736143167:AAE_v_fdmk0TlF6HfGaZjCrtdLgIjOC42vQ"
ADMIN_ID = 1043945034

bot = telebot.TeleBot(BOT_TOKEN)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📅 Забронировать смену", callback_data="book"))
    bot.send_message(message.chat.id, "Нажми кнопку, чтобы забронировать смену:", reply_markup=markup)

# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id, text="Кнопка нажата!", show_alert=True)
    if call.data == "book":
        bot.edit_message_text(
            "✅ Функция бронирования в разработке. Скоро будет готова!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.send_message(ADMIN_ID, f"Пользователь {call.from_user.first_name} нажал кнопку бронирования.")

print("Бот успешно запущен и слушает сообщения...")
bot.infinity_polling()
