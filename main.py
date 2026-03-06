import telebot
from telebot import types
import time
import threading

# তোর টোকেন এবং এডমিন আইডি
API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 7364617700

# ডিফল্ট অ্যাড লিংক (তুই পরে এটা পাল্টাতে পারবি)
current_ad_link = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

user_data = {}
user_list = []

def get_user(chat_id, name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list:
            user_list.append(chat_id)
        user_data[chat_id] = {'balance': 0.0, 'referrals': 0, 'status': False, 'name': name, 'no': len(user_list)}
    return user_data[chat_id]

# টাইমার ফাংশন (বাটন এডিট করবে)
def start_timer(chat_id, message_id, task_no):
    for i in range(15, 0, -1):
        try:
            time.sleep(1)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f"⏳ Wait: {i}s", url=current_ad_link))
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)
        except: return
    
    user_data[chat_id]['status'] = True
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"done_{task_no}"))
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.chat.id, message.from_user.first_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(message.chat.id, f"Welcome {user['name']}! 🚀\nUID: {message.chat.id}\nStart earning now!", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        msg = "👨‍✈️ **Admin Panel**\n\n১. অ্যাড লিংক পাল্টাতে লিখুন: /setlink [লিংক]\n২. ইউজার লিস্ট দেখতে ক্লিক করুন।"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("👤 User List", "🔙 Back")
        bot.send_message(ADMIN_ID, msg, reply_markup=markup)

@bot.message_handler(commands=['setlink'])
def set_link(message):
    global current_ad_link
    if message.chat.id == ADMIN_ID:
        try:
            new_link = message.text.split()[1]
            current_ad_link = new_link
            bot.send_message(ADMIN_ID, f"✅ Ad Link Updated to:\n{new_link}")
        except:
            bot.send_message(ADMIN_ID, "❌ Error! Use: /setlink https://link.com")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if message.text == "🎯 Tasks":
        send_task(chat_id, 1)
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 **Profile Info**\n🆔 UID: `{chat_id}`\n🔢 User No: #{user['no']:03d}\n💰 Balance: ৳{round(user['balance'], 2)}")
    elif message.text == "👑 Leaderboard":
        top = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
        lb = "👑 **Top Earners**\n\n"
        for i, (uid, data) in enumerate(top, 1):
            lb += f"{i}. {data['name']} - ৳{round(data['balance'], 2)}\n"
        bot.send_message(chat_id, lb)
    elif message.text == "👤 User List" and chat_id == ADMIN_ID:
        msg = "📋 **User List:**\n"
        for uid, data in user_data.items():
            msg += f"N: {data['name']} | B: ৳{data['balance']}\n"
        bot.send_message(ADMIN_ID, msg)
    elif message.text == "🔙 Back":
        start(message)

def send_task(chat_id, task_no, message_id=None):
    user_data[chat_id]['status'] = False
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=current_ad_link, callback_data=f"go_{task_no}"))
    text = f"💡 **Task {task_no}/8**\nReward: ৳0.92\n\n১. 'View Ad' এ ক্লিক কর।\n২. ১৫ সেকেন্ড পর বাটনটি কনফার্ম হবে।"
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    chat_id = call.message.chat.id
    if "go_" in call.data:
        task_no = call.data.split("_")[-1]
        threading.Thread(target=start_timer, args=(chat_id, call.message.message_id, task_no)).start()
        bot.answer_callback_query(call.id, "Timer Started!")
    elif "done_" in call.data:
        if user_data[chat_id]['status']:
            num = int(call.data.split("_")[-1])
            if num < 8: send_task(chat_id, num + 1, call.message.message_id)
            else:
                user_data[chat_id]['balance'] += 0.92
                bot.edit_message_text("🎊 Success! You earned ৳0.92", chat_id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "⚠️ Wait for the timer!", show_alert=True)

bot.polling(none_stop=True)
            
