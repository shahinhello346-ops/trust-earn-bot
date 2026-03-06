import telebot
from telebot import types
import time
import threading

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

user_data = {}
user_list = []

def get_user(chat_id, name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list: user_list.append(chat_id)
        user_data[chat_id] = {'balance': 0.0, 'referrals': 0, 'status': False, 'name': name, 'uid': len(user_list)}
    return user_data[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.chat.id, message.from_user.first_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(message.chat.id, f"Welcome {user['name']}! 🚀\nStart earning now!", reply_markup=markup)

def timer_thread(chat_id, message_id, task_no):
    for i in range(15, 0, -1):
        try:
            time.sleep(1)
            bot.edit_message_text(f"⏳ Stay on Ad page: {i}s left...", chat_id, message_id)
        except: return
    
    # সময় শেষ হলে কনফার্ম বাটন আসবে
    user_data[chat_id]['status'] = True
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"done_{task_no}"))
    bot.edit_message_text("✅ Time Finished! Press Confirm to earn.", chat_id, message_id, reply_markup=markup)

def send_task(chat_id, task_no, message_id=None):
    user_data[chat_id]['status'] = False
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data=f"start_timer_{task_no}"))
    text = f"💡 **Task {task_no}/8**\nReward: ৳0.92\n\n1. Click 'View Ad'\n2. Watch for 15 seconds"
    
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data.startswith("start_timer_"):
        task_no = call.data.split("_")[-1]
        bot.answer_callback_query(call.id, "Timer Started!")
        # আলাদা থ্রেডে টাইমার চলবে যেন বট হ্যাং না হয়
        threading.Thread(target=timer_thread, args=(chat_id, call.message.message_id, task_no)).start()
        
    elif call.data.startswith("done_"):
        if user_data[chat_id]['status']:
            num = int(call.data.split("_")[-1])
            if num < 8:
                send_task(chat_id, num + 1, call.message.message_id)
            else:
                user_data[chat_id]['balance'] += 0.92
                bot.edit_message_text("🎊 Success! You earned ৳0.92", chat_id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ Wait for the timer!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    if message.text == "🎯 Tasks": send_task(chat_id, 1)
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 **Profile Info**\n🆔 UID: `{chat_id}`\n🔢 User No: #{user['uid']:03d}\n💰 Balance: ৳{round(user['balance'], 2)}")
    elif message.text == "👑 Leaderboard":
        top = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
        msg = "👑 **Top Earners**\n\n"
        for i, (u_id, data) in enumerate(top, 1): msg += f"{i}. {data['name']} - ৳{data['balance']}\n"
        bot.send_message(chat_id, msg)

bot.polling(none_stop=True)
        
