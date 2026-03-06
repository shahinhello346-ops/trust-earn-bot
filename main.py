import telebot
from telebot import types
from flask import Flask
from threading import Thread
import time

# --- Render Port Fix ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 7364617700
AD_LINK = 'https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c'

# তোর চ্যানেলের ইউজারনেমগুলো এখানে (বিনা @ চিহ্নে)
CHANNELS = ['TrustEarnCashOfficial', 'TrustEarnCashPayments', 'TrustEarnCashSupportGroup']

user_data = {}
user_list = []

def get_user(chat_id, name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list: user_list.append(chat_id)
        user_data[chat_id] = {'balance': 0.0, 'referrals': 0, 'name': name, 'no': len(user_list), 'tasks_done': 0, 'last_click': 0, 'is_banned': False}
    return user_data[chat_id]

def check_join(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(f"@{channel}", user_id).status
            if status == 'left': return False
        except: return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if not check_join(chat_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Official Channel", url="https://t.me/TrustEarnCashOfficial"))
        markup.add(types.InlineKeyboardButton("💰 Payment Proof", url="https://t.me/TrustEarnCashPayments"))
        markup.add(types.InlineKeyboardButton("💬 Support Group", url="https://t.me/TrustEarnCashSupportGroup"))
        markup.add(types.InlineKeyboardButton("✅ Joined - Click Here", callback_data="check_status"))
        bot.send_message(chat_id, f"Hello {user['name']}!\n\nYou must join our 3 channels to use this bot.", reply_markup=markup)
        return

    main_menu(chat_id, user)

def main_menu(chat_id, user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome Back {user['name']}! 🚀\nStart earning now!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)

    if call.data == "check_status":
        if check_join(chat_id):
            bot.delete_message(chat_id, call.message.message_id)
            main_menu(chat_id, user)
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined all channels yet!")

    elif call.data.startswith("confirm_"):
        now = time.time()
        if now - user['last_click'] < 15:
            bot.answer_callback_query(call.id, "⚠️ Stay on ad for 15s!")
            bot.send_message(ADMIN_ID, f"🚨 CHEATING ALERT!\nUser: {user['name']}\nID: {chat_id}")
            return
        
        user['last_click'] = now
        task_no = int(call.data.split("_")[1])
        if task_no < 8:
            send_task(chat_id, task_no + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            bot.edit_message_text("🎊 Done! ৳0.92 added.", chat_id, call.message.message_id)

    elif call.data.startswith("method_"):
        method = call.data.split("_")[1]
        msg = bot.send_message(chat_id, f"Enter your {method} number and Amount:")
        bot.register_next_step_handler(msg, process_withdraw, method)

def process_withdraw(message, method):
    chat_id = message.chat.id
    user = get_user(chat_id)
    bot.send_message(ADMIN_ID, f"🔔 WITHDRAW!\nUser: {user['name']}\nID: {chat_id}\nMethod: {method}\nInfo: {message.text}")
    bot.send_message(chat_id, "✅ Request sent! Wait 24h.")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    if not check_join(chat_id): return

    if message.text == "🎯 Tasks": 
        user['last_click'] = time.time()
        send_task(chat_id, 1)
    elif message.text == "💰 Wallet":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Bkash", callback_data="method_Bkash"), types.InlineKeyboardButton("Nagad", callback_data="method_Nagad"))
        bot.send_message(chat_id, f"💰 Balance: ৳{round(user['balance'], 2)}\nSelect Method:", reply_markup=markup)
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 PROFILE\n🏷 Name: {user['name']}\n🆔 ID: {chat_id}\n🔢 Member No: #{user['no']}\n💰 Balance: ৳{round(user['balance'], 2)}")
    elif message.text == "👫 Referral":
        bot.send_message(chat_id, f"👫 Referral Link: https://t.me/TrustEarnCash_bot?start={chat_id}")
    elif message.text == "👑 Leaderboard":
        bot.send_message(chat_id, "👑 Leaderboard coming soon!")

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"confirm_{task_no}"))
    text = f"💡 TASK: {task_no}/8\n💰 Reward: ৳0.92\nView ad for 15s."
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(none_stop=True)
