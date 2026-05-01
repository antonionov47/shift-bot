import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8736143167:AAE_v_fdmk0TlF6HfGaZjCrtdLgIjOC42vQ"
ADMIN_ID = 1043945034   # замените на свой реальный ID

bot = telebot.TeleBot(BOT_TOKEN)

# Ключевые строки: отключаем webhook и используем обычный polling
bot.remove_webhook()
print("Webhook removed, using polling...")

# Меню
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📅 Забронировать смену", callback_data="book"))
    bot.send_message(message.chat.id, "Нажми кнопку:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id, text="Кнопка сработала!")
    if call.data == "book":
        bot.edit_message_text("✅ Вы нажали кнопку. Функция бронирования в разработке.",
                              chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(ADMIN_ID, f"Пользователь {call.from_user.first_name} нажал кнопку.")

# Запуск с повышенным таймаутом
if __name__ == "__main__":
    print("Бот запущен")
    bot.infinity_polling(timeout=120, long_polling_timeout=120)
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

BOT_TOKEN = "8736143167:AAE_v_fdmk0TlF6HfGaZjCrtdLgIjOC42vQ"
ADMIN_ID = 1043945034

bot = telebot.TeleBot(BOT_TOKEN)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📅 Забронировать смену", callback_data="book"))
    bot.send_message(message.chat.id, "Нажми кнопку:", reply_markup=markup)

# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    # Сразу отправляем уведомление, что кнопка нажата
    bot.answer_callback_query(call.id, text="Кнопка нажата!", show_alert=True)
    # Меняем текст сообщения
    bot.edit_message_text("✅ Вы нажали кнопку бронирования. Функция в разработке.",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id)
    # Отправляем админу отчёт
    bot.send_message(ADMIN_ID, f"Пользователь {call.from_user.first_name} нажал кнопку.")

# Запуск
print("Бот запущен")
bot.infinity_polling(timeout=60)