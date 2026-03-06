import telebot
from telebot import types
import time
import threading

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7364617700
AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

# ডাটাবেজ ফিক্স
user_data = {}
user_list = []

def get_user(chat_id, name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list:
            user_list.append(chat_id)
        user_data[chat_id] = {
            'balance': 0.0, 
            'referrals': 0, 
            'status': False, 
            'name': name,
            'no': len(user_list)
        }
    return user_data[chat_id]

# টাইমার ফিক্স - বাটন নিজেই কাউন্ট করবে
def start_timer(chat_id, message_id, task_no):
    for i in range(15, 0, -1):
        try:
            time.sleep(1)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f"⏳ Wait: {i}s", url=AD_LINK))
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)
        except: return
    
    # ১৫ সেকেন্ড পর কনফার্ম বাটন নিশ্চিতভাবে আসবে
    user_data[chat_id]['status'] = True
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"done_{task_no}"))
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.chat.id, message.from_user.first_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(message.chat.id, f"Welcome {user['name']}! 🚀\nStart earning now!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if message.text == "🎯 Tasks":
        send_task(chat_id, 1)
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 **Profile**\n🆔 UID: `{chat_id}`\n🔢 User No: #{user['no']:03d}\n💰 Balance: ৳{round(user['balance'], 2)}")
    elif message.text == "💰 Wallet":
        bot.send_message(chat_id, f"💰 **Wallet**\nBalance: ৳{round(user['balance'], 2)}\nMin. Withdraw: ৳100")
    elif message.text == "👑 Leaderboard":
        top = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
        lb = "👑 **Top 10 Earners**\n\n"
        for i, (uid, data) in enumerate(top, 1):
            lb += f"{i}. {data['name']} - ৳{round(data['balance'], 2)}\n"
        bot.send_message(chat_id, lb)
    elif message.text == "👫 Referral":
        link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"👫 Invite friends and earn ৳3.00!\n\nLink: {link}")

def send_task(chat_id, task_no, message_id=None):
    user_data[chat_id]['status'] = False
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data=f"go_{task_no}"))
    text = f"💡 **Task {task_no}/8**\nReward: ৳0.92\n\n১. 'View Ad' এ ক্লিক কর।\n২. ১৫ সেকেন্ড বাটনটি কাউন্ট করবে।"
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
            bot.answer_callback_query(call.id, "⚠️ Please wait for the timer!", show_alert=True)

bot.polling(none_stop=True)
    
