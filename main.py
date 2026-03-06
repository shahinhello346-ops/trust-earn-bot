import telebot
from telebot import types
from flask import Flask
from threading import Thread
import time

# --- Render Port Fix (Flask) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
# ------------------------------

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 7364617700
AD_LINK = 'https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c'

user_data = {}
user_list = []

def get_user(chat_id, name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list: 
            user_list.append(chat_id)
        user_data[chat_id] = {
            'balance': 0.0, 
            'referrals': 0, 
            'name': name, 
            'no': len(user_list), 
            'ref_by': None, 
            'tasks_done': 0,
            'last_click_time': 0,
            'is_banned': False
        }
    return user_data[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if user['is_banned']:
        bot.send_message(chat_id, "❌ You are BANNED for violating rules!")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome {user['name']}! 🚀\nEarn ৳0.92 for every 8 tasks completed!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)

    if user['is_banned']:
        bot.answer_callback_query(call.id, "You are banned!")
        return

    # --- চিটিং ডিটেকশন (Cheating Detection) ---
    current_time = time.time()
    # যদি ১৫ সেকেন্ডের আগে কেউ কনফার্ম বাটনে ক্লিক করে
    if call.data.startswith("confirm_"):
        if current_time - user['last_click_time'] < 15:
            bot.answer_callback_query(call.id, "⚠️ Warning! Stay on the ad for 15s!")
            # অ্যাডমিনকে অ্যালার্ট পাঠানো
            bot.send_message(ADMIN_ID, f"🚨 CHEATING ALERT!\nUser: {user['name']}\nID: {chat_id}\nReason: Clicking Confirm too fast!")
            return
        
        user['last_click_time'] = current_time
        task_no = int(call.data.split("_")[1])
        user['tasks_done'] = task_no
        
        if task_no < 8:
            send_task(chat_id, task_no + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! 8 tasks completed. ৳0.92 added.", chat_id, call.message.message_id)

    elif call.data.startswith("method_"):
        method = call.data.split("_")[1]
        if user['balance'] < 100:
            bot.answer_callback_query(call.id, "Minimum balance ৳100 required!")
        else:
            msg = bot.send_message(chat_id, f"Enter your {method} number and Amount:")
            bot.register_next_step_handler(msg, process_withdraw, method)

def process_withdraw(message, method):
    chat_id = message.chat.id
    user = get_user(chat_id)
    bot.send_message(ADMIN_ID, f"🔔 WITHDRAW REQUEST!\nUser: {user['name']}\nID: {chat_id}\nMethod: {method}\nDetails: {message.text}")
    bot.send_message(chat_id, "✅ Request sent! Waiting for approval.")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if user['is_banned']: return

    if message.text == "🎯 Tasks": 
        user['last_click_time'] = time.time() # টাস্ক শুরু করার সময় রেকর্ড
        send_task(chat_id, 1)
    elif message.text == "💰 Wallet":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Bkash", callback_data="method_Bkash"), 
                   types.InlineKeyboardButton("Nagad", callback_data="method_Nagad"))
        bot.send_message(chat_id, f"💰 Balance: ৳{round(user['balance'], 2)}\nSelect Method:", reply_markup=markup)
    elif message.text == "👤 Profile":
        profile_msg = (f"👤 USER PROFILE\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"🏷 Name: {user['name']}\n"
                       f"🆔 User ID: {chat_id}\n"
                       f"🔢 Member No: #{user['no']}\n"
                       f"💰 Balance: ৳{round(user['balance'], 2)}\n"
                       f"👫 Referrals: {user['referrals']}")
        bot.send_message(chat_id, profile_msg)
    elif message.text == "👫 Referral":
        link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"👫 Earn ৳3.00 per referral!\nLink: {link}")
    elif message.text == "👑 Leaderboard":
        bot.send_message(chat_id, "👑 Leaderboard is being updated!")

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"confirm_{task_no}"))
    text = f"💡 TASK: {task_no}/8\n💰 Reward: ৳0.92\nView ad for 15s then click Confirm."
    if message_id: 
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: 
        bot.send_message(chat_id, text, reply_markup=markup)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(none_stop=True)
        
