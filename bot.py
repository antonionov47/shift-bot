import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import json
import os

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8736143167:AAE_v_fdmk0TlF6HfGaZjCrtdLgIjOC42vQ"
ADMIN_ID = 1043945034
DATA_FILE = "requests.json"
# ====================

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище заявок
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        requests = json.load(f)
else:
    requests = {}

next_id = max([int(k) for k in requests.keys()], default=0) + 1

# Функция сохранения заявок
def save_requests():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)

# Главное меню (ReplyKeyboard)
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📅 Забронировать смену"),
        KeyboardButton("📋 Мои заявки"),
        KeyboardButton("📞 Поддержка"),
        KeyboardButton("ℹ️ Помощь")
    )
    bot.send_message(
        message.chat.id,
        "✨ *Добро пожаловать!* ✨\n\n"
        "Я помогу быстро забронировать рабочую смену.\n\n"
        "👇 *Выбери действие:*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Обработка кнопок главного меню
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📅 Забронировать смену":
        show_calendar(message.chat.id)
    elif message.text == "📋 Мои заявки":
        show_my_requests(message.chat.id, message.from_user.id)
    elif message.text == "📞 Поддержка":
        bot.send_message(message.chat.id, "📞 *По вопросам пишите администратору:* @admin", parse_mode="Markdown")
    elif message.text == "ℹ️ Помощь":
        bot.send_message(
            message.chat.id,
            "ℹ️ *Помощь*\n\n"
            "1. Нажмите «Забронировать смену»\n"
            "2. Выберите дату из календаря\n"
            "3. Выберите время начала и окончания\n"
            "4. Дождитесь подтверждения администратора\n\n"
            "Статус заявок можно посмотреть в «Мои заявки»",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "❌ Используйте кнопки меню.")

# Показать календарь
def show_calendar(chat_id, year=None, month=None):
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    markup = InlineKeyboardMarkup(row_width=7)
    
    # Название месяца и кнопки переключения
    month_names = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
    title_row = [
        InlineKeyboardButton("◀️", callback_data=f"prev_{year}_{month}"),
        InlineKeyboardButton(f"{month_names[month-1]} {year}", callback_data="ignore"),
        InlineKeyboardButton("▶️", callback_data=f"next_{year}_{month}")
    ]
    markup.row(*title_row)
    
    # Дни недели
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    markup.row(*[InlineKeyboardButton(day, callback_data="ignore") for day in week_days])
    
    # Дни месяца
    first_day = datetime(year, month, 1)
    start_weekday = first_day.weekday()  # 0 = понедельник
    
    last_day = (datetime(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31
    
    # Пустые дни
    row = []
    for _ in range(start_weekday):
        row.append(InlineKeyboardButton(" ", callback_data="ignore"))
    
    for day in range(1, last_day + 1):
        date_obj = datetime(year, month, day)
        # Прошлые даты недоступны
        if date_obj.date() < now.date():
            row.append(InlineKeyboardButton(str(day), callback_data="ignore"))
        else:
            row.append(InlineKeyboardButton(str(day), callback_data=f"date_{year}_{month}_{day}"))
        
        if len(row) == 7:
            markup.row(*row)
            row = []
    
    if row:
        while len(row) < 7:
            row.append(InlineKeyboardButton(" ", callback_data="ignore"))
        markup.row(*row)
    
    bot.send_message(chat_id, "📅 *Выберите дату смены:*", reply_markup=markup, parse_mode="Markdown")

# Обработка callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    
    if data == "ignore":
        bot.answer_callback_query(call.id)
        return
    
    # Переключение месяца
    elif data.startswith("prev_"):
        _, year, month = data.split("_")
        year, month = int(year), int(month)
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        bot.edit_message_text("📅 Загрузка...", chat_id=call.message.chat.id, message_id=call.message.message_id)
        show_calendar(call.message.chat.id, year, month)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    
    elif data.startswith("next_"):
        _, year, month = data.split("_")
        year, month = int(year), int(month)
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        bot.edit_message_text("📅 Загрузка...", chat_id=call.message.chat.id, message_id=call.message.message_id)
        show_calendar(call.message.chat.id, year, month)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Выбор даты
    elif data.startswith("date_"):
        _, year, month, day = data.split("_")
        date_str = f"{day}.{month}.{year}"
        
        # Создаём временные данные для пользователя
        if not hasattr(callback_handler, "temp_data"):
            callback_handler.temp_data = {}
        callback_handler.temp_data[user_id] = {"date": date_str}
        
        # Выбор времени начала
        markup = InlineKeyboardMarkup(row_width=4)
        for hour in range(8, 23):
            markup.add(InlineKeyboardButton(f"{hour}:00", callback_data=f"start_{hour}:00"))
        bot.edit_message_text(
            f"📅 *Дата:* {date_str}\n\n🕐 *Выберите время начала смены:*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    
    # Выбор времени начала
    elif data.startswith("start_"):
        start_time = data.split("_")[1]
        callback_handler.temp_data[user_id]["start"] = start_time
        
        # Выбор времени окончания
        markup = InlineKeyboardMarkup(row_width=4)
        start_hour = int(start_time.split(":")[0])
        for hour in range(start_hour + 1, 24):
            markup.add(InlineKeyboardButton(f"{hour}:00", callback_data=f"end_{hour}:00"))
        bot.edit_message_text(
            f"📅 *Дата:* {callback_handler.temp_data[user_id]['date']}\n"
            f"🕐 *Начало:* {start_time}\n\n"
            f"🕑 *Выберите время окончания:*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    
    # Выбор времени окончания
    elif data.startswith("end_"):
        end_time = data.split("_")[1]
        date = callback_handler.temp_data[user_id]["date"]
        start = callback_handler.temp_data[user_id]["start"]
        
        global next_id
        rid = next_id
        next_id += 1
        
        requests[rid] = {
            "user_id": user_id,
            "user_name": user_name,
            "date": date,
            "start": start,
            "end": end_time,
            "status": "pending"
        }
        save_requests()
        
        # Уведомление пользователю
        bot.edit_message_text(
            f"✅ *Заявка #{rid} отправлена!*\n\n"
            f"📅 {date}\n"
            f"🕐 {start} - {end_time}\n\n"
            f"Ожидайте подтверждения от администратора.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        
        # Уведомление администратору
        admin_markup = InlineKeyboardMarkup()
        admin_markup.add(
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_{rid}"),
            InlineKeyboardButton("❌ Отказать", callback_data=f"reject_{rid}")
        )
        bot.send_message(
            ADMIN_ID,
            f"🔔 *НОВАЯ ЗАЯВКА #{rid}*\n\n"
            f"👤 *Сотрудник:* {user_name}\n"
            f"📅 *Дата:* {date}\n"
            f"🕐 *Время:* {start} - {end_time}",
            reply_markup=admin_markup,
            parse_mode="Markdown"
        )
        
        del callback_handler.temp_data[user_id]
    
    # Обработка решения администратора
    elif data.startswith("approve_"):
        rid = int(data.split("_")[1])
        if rid in requests:
            requests[rid]["status"] = "approved"
            save_requests()
            bot.send_message(
                requests[rid]["user_id"],
                f"✅ *СМЕНА ПОДТВЕРЖДЕНА!*\n\n"
                f"📅 {requests[rid]['date']}\n"
                f"🕐 {requests[rid]['start']} - {requests[rid]['end']}\n\n"
                f"Хорошего рабочего дня! 🎉",
                parse_mode="Markdown"
            )
            bot.edit_message_text(
                f"✅ Заявка #{rid} подтверждена",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        bot.answer_callback_query(call.id)
    
    elif data.startswith("reject_"):
        rid = int(data.split("_")[1])
        if rid in requests:
            requests[rid]["status"] = "rejected"
            save_requests()
            bot.send_message(
                requests[rid]["user_id"],
                f"❌ *СМЕНА ОТКЛОНЕНА*\n\n"
                f"📅 {requests[rid]['date']}\n\n"
                f"Попробуйте выбрать другое время.",
                parse_mode="Markdown"
            )
            bot.edit_message_text(
                f"❌ Заявка #{rid} отклонена",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        bot.answer_callback_query(call.id)

# Показать заявки пользователя
def show_my_requests(chat_id, user_id):
    user_requests = [r for r in requests.values() if r["user_id"] == user_id]
    if not user_requests:
        bot.send_message(chat_id, "📋 *У вас пока нет заявок.*", parse_mode="Markdown")
        return
    
    msg = "📋 *Ваши заявки:*\n\n"
    for r in user_requests:
        status_emoji = "⏳" if r["status"] == "pending" else ("✅" if r["status"] == "approved" else "❌")
        status_text = "ожидает" if r["status"] == "pending" else ("подтверждена" if r["status"] == "approved" else "отклонена")
        msg += f"{status_emoji} *{r['date']}* {r['start']} - {r['end']} — {status_text}\n"
    bot.send_message(chat_id, msg, parse_mode="Markdown")

print("✅ Бот запущен!")
bot.infinity_polling()
