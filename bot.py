import telebot
import time

# ===== НАСТРОЙКИ (ЗАМЕНИТЕ НА СВОИ) =====
BOT_TOKEN = "8736143167:AAE_v_fdmk0TlF6HfGaZjCrtdLgIjOC42vQ"  # ← ваш токен
ADMIN_ID = 1043945034  # ← ваш Telegram ID
# =========================================

bot = telebot.TeleBot(BOT_TOKEN)

requests = {}
next_id = 1

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
        "👋 Бот для бронирования смен\n\nНапиши: хочу смену на 15.05.2026 с 9:00 до 18:00")

@bot.message_handler(func=lambda m: m.chat.id != ADMIN_ID)
def handle_request(m):
    global next_id
    text = m.text.lower()
    
    if "хочу смену" not in text:
        bot.send_message(m.chat.id, "❌ Напишите: хочу смену на 15.05.2026 с 9:00 до 18:00")
        return
    
    try:
        date = text.split("на")[1].split()[0]
        times = text.split("с")[1].split("до")
        start = times[0].strip()
        end = times[1].split()[0].strip()
        
        rid = next_id
        next_id += 1
        requests[rid] = {"user": m.from_user.first_name, "date": date, "start": start, "end": end}
        
        bot.send_message(ADMIN_ID, f"🔔 #{rid} от {m.from_user.first_name}\n📅 {date} {start}-{end}\n\n✅ /approve_{rid}\n❌ /reject_{rid}")
        bot.send_message(m.chat.id, f"✅ Заявка #{rid} отправлена")
    except:
        bot.send_message(m.chat.id, "❌ Ошибка. Формат: хочу смену на 15.05.2026 с 9:00 до 18:00")

@bot.message_handler(commands=['approve', 'reject'])
def admin_decision(m):
    if m.chat.id != ADMIN_ID:
        return
    action, rid = m.text.split('_')
    rid = int(rid)
    if rid not in requests:
        bot.send_message(ADMIN_ID, f"Заявка {rid} не найдена")
        return
    req = requests[rid]
    if "approve" in action:
        bot.send_message(req["user"], f"✅ Смена на {req['date']} {req['start']}-{req['end']} ПОДТВЕРЖДЕНА")
        bot.send_message(ADMIN_ID, f"✅ Заявка #{rid} подтверждена")
    else:
        bot.send_message(req["user"], f"❌ Смена на {req['date']} ОТКЛОНЕНА")
        bot.send_message(ADMIN_ID, f"❌ Заявка #{rid} отклонена")

print("Бот запущен")
bot.infinity_polling()