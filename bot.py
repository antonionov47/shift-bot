import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import json
import os
import calendar as cal

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

def get_month_name(month):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
              "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    return months[month - 1]

def create_calendar(year, month, selected_date=None):
    markup = InlineKeyboardMarkup(row_width=7)
    
    # Заголовок с месяцем и годом + кнопки навигации
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    today = now.day
    
    nav_buttons = [
        InlineKeyboardButton("◀️", callback_data=f"cal_prev_{year}_{month}"),
        InlineKeyboardButton(f"{get_month_name(month)} {year}", callback_data="ignore"),
        InlineKeyboardButton("▶️", callback_data=f"cal_next_{year}_{month}")
    ]
    markup.row(*nav_buttons)
    
    # Дни недели
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    markup.row(*[InlineKeyboardButton(day, callback_data="ignore") for day in weekdays])
    
    # Получаем первый день месяца и количество дней
    first_day = datetime(year, month, 1)
    start_weekday = first_day.weekday()
    days_in_month = cal.monthrange(year, month)[1]
    
    # Пустые ячейки до первого дня
    row = []
    for _ in range(start_weekday):
        row.append(InlineKeyboardButton(" ", callback_data="ignore"))
    
    # Дни месяца
    for day in range(1, days_in_month + 1):
        is_past = (year < current_year) or (year == current_year and month < current_month) or (year == current_year and month == current_month and day < today)
        
        if is_past:
            # Прошедшие дни — заблокированы
            row.append(InlineKeyboardButton("🔒", callback_data="ignore"))
        else:
            # Доступные дни
            row.append(InlineKeyboardButton(str(day), callback_data=f"date_{year}_{month}_{day}"))
        
        if len(row) == 7:
            markup.row(*row)
            row = []
    
    # Заполняем последнюю строку
    if row:
        while len(row) < 7:
            row.append(InlineKeyboardButton(" ", callback_data="ignore"))
        markup.row(*row)
    
    return markup

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
        "Я помогу вам быстро и удобно забронировать рабочую смену.\n\n"
        "👇 *Выберите действие:*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    text = message.text
    user_id = message.from_user.id
    
    if text == "📅 Забронировать смену":
        now = datetime.now()
        markup = create_calendar(now.year, now.month)
        bot.send_message(
            message.chat.id,
            "📅 *Выберите дату смены*\n\n"
            "🔒 — прошлые даты (недоступны)\n"
            "◀️ ▶️ — переключение месяцев",
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
                status = "⏳ Ожидает подтверждения"
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
            "📞 *Поддержка*\n\n"
            "По всем вопросам обращайтесь к администратору.",
            parse_mode="Markdown"
        )
    
    elif text == "ℹ️ Помощь":
        bot.send_message(
            message.chat.id,
            "ℹ️ *Помощь*\n\n"
            "1️⃣ Нажмите «Забронировать смену»\n"
            "2️⃣ Выберите удобную дату в календаре\n"
            "3️⃣ Выберите время начала смены\n"
            "4️⃣ Выберите время окончания смены\n"
            "5️⃣ Дождитесь подтверждения администратора\n\n"
            "Статус заявок можно посмотреть в «Мои заявки»",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "❌ *Используйте кнопки меню*", parse_mode="Markdown")

# Навигация по календарю
@bot.callback_query_handler(func=lambda call: call.data.startswith("cal_prev_") or call.data.startswith("cal_next_"))
def calendar_navigation(call):
    _, action, year, month = call.data.split("_")
    year, month = int(year), int(month)
    
    if action == "prev":
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
    else:
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
    
    markup = create_calendar(year, month)
    bot.edit_message_text(
        "📅 *Выберите дату смены*",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# Выбор даты
@bot.callback_query_handler(func=lambda call: call.data.startswith("date_"))
def select_date(call):
    _, year, month, day = call.data.split("_")
    year, month, day = int(year), int(month), int(day)
    date_str = f"{day:02d}.{month:02d}.{year}"
    
    # Сохраняем дату во временном хранилище
    user_id = call.from_user.id
    if user_id not in temp_data:
        temp_data[user_id] = {}
    temp_data[user_id]["date"] = date_str
    temp_data[user_id]["year"] = year
    temp_data[user_id]["month"] = month
    temp_data[user_id]["day"] = day
    
    # Кнопки для выбора времени начала (с 8:00 до 22:00)
    markup = InlineKeyboardMarkup(row_width=3)
    for hour in range(8, 23):
        markup.add(InlineKeyboardButton(f"{hour:02d}:00", callback_data=f"start_{hour:02d}:00"))
    
    bot.edit_message_text(
        f"📅 *Выбрана дата:* {date_str}\n\n"
        f"🕐 *Выберите время начала смены:*",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# Выбор времени начала
@bot.callback_query_handler(func=lambda call: call.data.startswith("start_"))
def select_start_time(call):
    start_time = call.data.split("_")[1]
    user_id = call.from_user.id
    
    temp_data[user_id]["start"] = start_time
    start_hour = int(start_time.split(":")[0])
    
    # Кнопки для выбора времени окончания (от start_hour+1 до 23)
    markup = InlineKeyboardMarkup(row_width=3)
    for hour in range(start_hour + 1, 24):
        markup.add(InlineKeyboardButton(f"{hour:02d}:00", callback_data=f"end_{hour:02d}:00"))
    
    bot.edit_message_text(
        f"📅 *Дата:* {temp_data[user_id]['date']}\n"
        f"🕐 *Начало:* {start_time}\n\n"
        f"🕑 *Выберите время окончания смены:*",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# Выбор времени окончания и создание заявки
@bot.callback_query_handler(func=lambda call: call.data.startswith("end_"))
def select_end_time(call):
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
    
    # Уведомление пользователю
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📋 Мои заявки", callback_data="my_requests"))
    
    bot.edit_message_text(
        f"✅ *Заявка #{rid} успешно отправлена!*\n\n"
        f"📅 *Дата:* {date}\n"
        f"🕐 *Время:* {start} - {end_time}\n\n"
        f"⏳ Ожидайте подтверждения администратора.\n\n"
        f"Статус заявки можно отследить в разделе «Мои заявки».",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
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
        f"🕐 *Время:* {start} - {end_time}\n"
        f"🕒 *Создана:* {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        reply_markup=admin_markup,
        parse_mode="Markdown"
    )
    
    del temp_data[user_id]
    bot.answer_callback_query(call.id)

# Просмотр заявок через кнопку
@bot.callback_query_handler(func=lambda call: call.data == "my_requests")
def show_requests(call):
    user_id = call.from_user.id
    user_requests = {k: v for k, v in requests.items() if v["user_id"] == user_id}
    
    if not user_requests:
        bot.edit_message_text(
            "📋 *У вас пока нет заявок*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
    else:
        msg = "📋 *Ваши заявки:*\n\n"
        for rid, r in user_requests.items():
            if r["status"] == "pending":
                status = "⏳ Ожидает"
            elif r["status"] == "approved":
                status = "✅ Подтверждена"
            else:
                status = "❌ Отклонена"
            msg += f"*#{rid}* | {r['date']} | {r['start']}-{r['end']} | {status}\n"
        bot.edit_message_text(
            msg,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
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
            f"📅 *Дата:* {req['date']}\n"
            f"🕐 *Время:* {req['start']} - {req['end']}\n\n"
            f"Желаем продуктивного рабочего дня! 💪",
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
            f"❌ *СМЕНА ОТКЛОНЕНА*\n\n"
            f"📅 *Дата:* {req['date']}\n\n"
            f"Попробуйте выбрать другое время.",
            parse_mode="Markdown"
        )
        
        bot.edit_message_text(
            f"❌ *Заявка #{rid} отклонена*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
    
    bot.answer_callback_query(call.id)

# Обработка игнорируемых callback (пустые кнопки)
@bot.callback_query_handler(func=lambda call: call.data == "ignore")
def ignore_callback(call):
    bot.answer_callback_query(call.id)

print("✅ Бот успешно запущен!")
bot.infinity_polling()
