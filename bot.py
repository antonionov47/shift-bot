import telebot

# ===== НАСТРОЙКИ (ЗАМЕНИТЕ НА СВОИ) =====
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"   # ← вставьте сюда свой токен (например: 123456:ABC-DEF)
ADMIN_ID = 123456789                   # ← вставьте свой Telegram ID (узнайте у @userinfobot)
# ========================================

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище заявок (в оперативной памяти, для простоты)
requests = {}
next_id = 1

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
        "👋 Бот для бронирования смен\n\n"
        "📝 Напиши: хочу смену на 15.05.2026 с 9:00 до 18:00")

# Обработка всех текстовых сообщений (включая администратора)
@bot.message_handler(func=lambda msg: True)
def handle_all_messages(message):
    # Игнорируем команды (начинающиеся с /)
    if message.text.startswith('/'):
        return

    global next_id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    text = message.text.lower()

    # Проверяем, что это запрос на смену
    if "хочу смену" in text:
        try:
            # Парсим дату (после слова "на")
            date_part = text.split("на")[1].split()[0]
            
            # Парсим время
            time_part = text.split("с")[1].split("до")
            start_time = time_part[0].strip()
            end_time = time_part[1].split()[0].strip()
            
            # Создаём заявку
            rid = next_id
            next_id += 1
            requests[rid] = {
                "user_id": user_id,
                "user_name": user_name,
                "date": date_part,
                "start": start_time,
                "end": end_time
            }
            
            # Отправляем подтверждение пользователю
            bot.send_message(user_id, f"✅ Заявка #{rid} отправлена администратору")
            
            # Отправляем уведомление администратору (с кнопками-командами)
            admin_text = (f"🔔 НОВАЯ ЗАЯВКА #{rid}\n\n"
                          f"👤 Сотрудник: {user_name}\n"
                          f"📅 Дата: {date_part}\n"
                          f"🕐 Время: {start_time} - {end_time}\n\n"
                          f"✅ /approve_{rid}\n"
                          f"❌ /reject_{rid}")
            bot.send_message(ADMIN_ID, admin_text)
            
        except Exception as e:
            bot.send_message(user_id,
                "❌ Ошибка. Напишите в формате:\n"
                "хочу смену на 16.05.2026 с 10:00 до 19:00")
    else:
        bot.send_message(user_id,
            "❌ Не понял. Напишите:\n"
            "хочу смену на 16.05.2026 с 10:00 до 19:00")

# Обработка команд администратора (approve / reject)
@bot.message_handler(commands=['approve', 'reject'])
def admin_decision(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")
        return
    
    # Разбираем команду, например: /approve_1
    command_parts = message.text.split('_')
    if len(command_parts) != 2:
        return
    
    action = command_parts[0].replace('/', '')  # approve или reject
    try:
        rid = int(command_parts[1])
    except ValueError:
        return
    
    if rid not in requests:
        bot.send_message(ADMIN_ID, f"❌ Заявка #{rid} не найдена")
        return
    
    req = requests[rid]
    
    if action == "approve":
        # Уведомляем сотрудника
        bot.send_message(req["user_id"],
            f"✅ ВАША СМЕНА ПОДТВЕРЖДЕНА!\n\n"
            f"📅 {req['date']} {req['start']} - {req['end']}\n\n"
            f"Хорошего рабочего дня!")
        # Уведомляем администратора
        bot.send_message(ADMIN_ID, f"✅ Заявка #{rid} подтверждена")
    else:
        # Отказ
        bot.send_message(req["user_id"],
            f"❌ Ваша смена на {req['date']} отклонена.")
        bot.send_message(ADMIN_ID, f"❌ Заявка #{rid} отклонена")
    
    # Удаляем обработанную заявку из памяти
    del requests[rid]

print("Бот запущен и слушает сообщения...")
bot.infinity_polling()