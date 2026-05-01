import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import json
import os

BOT_TOKEN = "8736143167:AAE_v_fdmk0TlF6HfGaZjCrtdLgIjOC42vQ"
ADMIN_ID = 1043945034
DATA_FILE = "requests.json"

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        requests = json.load(f)
else:
    requests = {}

next_id = max([int(k) for k in requests.keys()], default=0) + 1
temp_data = {}

def save_requests():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)

# Простой календарь — только доступные дни (сегодня + 14 дней)
def get_available_dates():
    dates = []
    today = datetime.now().date()
    for i in range(14):
        date = today + timedelta(days=i)
        dates.append(date.strftime("%d.%m.%Y"))
    return dates

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
        "✨ *Добро пожаловать в сервис бронирования смен!* ✨\n\n"
        "👇 *Выберите действие:*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    text = message.text
    user_id = message.from_user.id
    
    if text == "📅 Забронировать смену":
        dates = get_available_dates()
        markup = InlineKeyboardMarkup(row_width=2)
        for date in dates:
            markup.add(InlineKeyboardButton(date, callback_data=f"date_{date}"))
        bot.send_message(
            message.chat.id,
            "📅 *Выберите дату смены:*\n\n"
            "Доступны даты на ближайшие 14 дней",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    
    elif text == "📋 Мои заявки":
        user_requests = {k: v for k, v in requests.items() if v["user_id"] == user_id}
        if not user_requests:
            bot.send_message(message.chat.id, "📋 *У вас пока нет заявок*", parse_mode="Markdown")
            return
        
        msg = "📋 *Ваши заявки:*\n\n"
        for rid, r in user_requests.items():
            if r["status"] == "pending":
                status = "⏳ Ожидает"
                emoji = "⏳"
            elif r["status"] == "approved":
                status = "✅ Подтверждена"
                emoji = "✅"
            else:
                status = "❌ Отклонена"
                emoji = "❌"
            msg += f"{emoji} *Заявка #{rid}*\n"
            msg += f"   📅 {r['date']}\n"
            msg += f"   🕐 {r['start']} - {r['end']}\n"
            msg += f"   📍 {status}\n\n"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    
    elif text == "📞 Поддержка":
        bot.send_message(
            message.chat.id,
            "📞 *Поддержка*\n\nПо всем вопросам обращайтесь к администратору.",
            parse_mode="Markdown"
        )
    
    elif text == "ℹ️ Помощь":
        bot.send_message(
            message.chat.id,
            "ℹ️ *Помощь*\n\n"
            "1️⃣ Нажмите «Забронировать смену»\n"
            "2️⃣ Выберите удобную дату\n"
            "3️⃣ Выберите время начала\n"
            "4️⃣ Выберите время окончания\n"
            "5️⃣ Дождитесь подтверждения",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "❌ *Используйте кнопки меню*", parse_mode="Markdown")

# Выбор даты
@bot.callback_query_handler(func=lambda call: call.data.startswith("date_"))
def select_date(call):
    date = call.data.split("_")[1]
    user_id = call.from_user.id
    
    temp_data[user_id] = {"date": date}
    
    markup = InlineKeyboardMarkup(row_width=3)
    for hour in range(8, 23):
        markup.add(InlineKeyboardButton(f"{hour:02d}:00", callback_data=f"start_{hour:02d}:00"))
    
    bot.edit_message_text(
        f"📅 *Дата:* {date}\n\n"
        f"🕐 *Выберите время начала:*",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# Выбор времени начала
@bot.callback_query_handler(func=lambda call: call.data.startswith("start_"))
def select_start(call):
    start_time = call.data.split("_")[1]
    user_id = call.from_user.id
    
    temp_data[user_id]["start"] = start_time
    start_hour = int(start_time.split(":")[0])
    
    markup = InlineKeyboardMarkup(row_width=3)
    for hour in range(start_hour + 1, 24):
        markup.add(InlineKeyboardButton(f"{hour:02d}:00", callback_data=f"end_{hour:02d}:00"))
    
    bot.edit_message_text(
        f"📅 *Дата:* {temp_data[user_id]['date']}\n"
        f"🕐 *Начало:* {start_time}\n\n"
        f"🕑 *Выберите время окончания:*",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# Выбор времени окончания и создание заявки
@bot.callback_query_handler(func=lambda call: call.data.startswith("end_"))
def select_end(call):
    end_time = call.data.split("_")[1]
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    
    date = temp_data[user_id]["date"]
    start = temp_data[user_id]["start"]
    
    global next_id
    rid = next_id
    next_id += 1
    
    requests[str(rid)] = {
        "user_id": user_id,
        "user_name": user_name,
        "date": date,
        "start": start,
        "end": end_time,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_requests()
    
    bot.edit_message_text(
        f"✅ *Заявка #{rid} отправлена!*\n\n"
        f"📅 {date}\n"
        f"🕐 {start} - {end_time}\n\n"
        f"Ожидайте подтверждения.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    
    # Уведомление администратору
    admin_markup = InlineKeyboardMarkup()
    admin_markup.row(
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
    
    del temp_data[user_id]
    bot.answer_callback_query(call.id)

# Обработка действий администратора
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def admin_decision(call):
    action, rid = call.data.split("_")
    
    if rid not in requests:
        bot.answer_callback_query(call.id, "Заявка не найдена", show_alert=True)
        return
    
    req = requests[rid]
    
    if action == "approve":
        req["status"] = "approved"
        save_requests()
        
        bot.send_message(
            req["user_id"],
            f"✅ *СМЕНА ПОДТВЕРЖДЕНА!* 🎉\n\n"
            f"📅 {req['date']}\n"
            f"🕐 {req['start']} - {req['end']}\n\n"
            f"Хорошего рабочего дня!",
            parse_mode="Markdown"
        )
        bot.edit_message_text(
            f"✅ *Заявка #{rid} подтверждена*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
    else:
        req["status"] = "rejected"
        save_requests()
        
        bot.send_message(
            req["user_id"],
            f"❌ *СМЕНА ОТКЛОНЕНА*\n\n📅 {req['date']}\n\nПопробуйте другую дату.",
            parse_mode="Markdown"
        )
        bot.edit_message_text(
            f"❌ *Заявка #{rid} отклонена*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
    
    bot.answer_callback_query(call.id)

print("✅ Бот запущен!")
bot.infinity_polling()
