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

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 7364617700
AD_LINK = 'https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c'
CHANNELS = ['TrustEarnCashOfficial', 'TrustEarnCashPayments', 'TrustEarnCashSupportGroup']

user_data = {}
user_list = []

def get_user(chat_id, first_name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list: user_list.append(chat_id)
        user_data[chat_id] = {'balance': 0.0, 'referrals': 0, 'name': first_name, 'no': len(user_list), 'last_click': 0, 'tasks_today': 0, 'last_bonus': 0}
    if user_data[chat_id]['name'] == "User" and first_name != "User":
        user_data[chat_id]['name'] = first_name
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
        markup.add(types.InlineKeyboardButton("📢 Channel", url="https://t.me/TrustEarnCashOfficial"),
                   types.InlineKeyboardButton("💰 Payment", url="https://t.me/TrustEarnCashPayments"))
        markup.add(types.InlineKeyboardButton("✅ Joined - Click Here", callback_data="check_status"))
        bot.send_message(chat_id, f"Hello {user['name']}!\nJoin our channels to earn.", reply_markup=markup)
        return
    main_menu(chat_id)

def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "🎁 Daily Bonus", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, "Main Menu 🚀", reply_markup=markup)

# --- Admin Controls ---
@bot.message_handler(commands=['add'], func=lambda m: m.from_user.id == ADMIN_ID)
def add_bal(message):
    try:
        _, uid, amt = message.text.split()
        user_data[int(uid)]['balance'] += float(amt)
        bot.reply_to(message, f"✅ Added ৳{amt} to {uid}")
    except: bot.reply_to(message, "Use: /add <id> <amount>")

@bot.message_handler(commands=['cut'], func=lambda m: m.from_user.id == ADMIN_ID)
def cut_bal(message):
    try:
        _, uid, amt = message.text.split()
        user_data[int(uid)]['balance'] -= float(amt)
        bot.reply_to(message, f"❌ Deducted ৳{amt} from {uid}")
    except: bot.reply_to(message, "Use: /cut <id> <amount>")

@bot.message_handler(commands=['info'], func=lambda m: m.from_user.id == ADMIN_ID)
def user_info(message):
    try:
        _, uid = message.text.split()
        u = user_data[int(uid)]
        bot.reply_to(message, f"👤 User: {u['name']}\n💰 Bal: ৳{u['balance']}\n🎯 Tasks: {u['tasks_today']}")
    except: bot.reply_to(message, "Use: /info <id>")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    if call.data == "check_status":
        if check_join(chat_id):
            bot.delete_message(chat_id, call.message.message_id)
            main_menu(chat_id)
        else: bot.answer_callback_query(call.id, "❌ Join first!")

    elif call.data.startswith("confirm_"):
        now = time.time()
        if now - user['last_click'] < 15:
            bot.answer_callback_query(call.id, "⚠️ Wait 15s!")
            return
        user['last_click'] = now
        task_no = int(call.data.split("_")[1])
        if task_no < 8: send_task(chat_id, task_no + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            user['tasks_today'] += 1
            bot.edit_message_text("🎊 ৳0.92 Added!", chat_id, call.message.message_id)

    elif call.data.startswith("method_"):
        method = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("৳১০০", callback_data=f"amt_{method}_100"),
                   types.InlineKeyboardButton("৳২০০", callback_data=f"amt_{method}_200"))
        bot.edit_message_text(f"Select {method} amount:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("amt_"):
        _, method, amount = call.data.split("_")
        if user['balance'] < float(amount):
            bot.answer_callback_query(call.id, "❌ No balance!")
            return
        msg = bot.send_message(chat_id, f"Enter {method} Number:")
        bot.register_next_step_handler(msg, final_withdraw, method, amount)

def final_withdraw(message, method, amount):
    chat_id = message.chat.id
    user = get_user(chat_id)
    user['balance'] -= float(amount)
    bot.send_message(ADMIN_ID, f"💰 WITHDRAW!\nUser: {user['name']}\nID: {chat_id}\nMethod: {method}\nAmount: ৳{amount}\nNum: {message.text}")
    bot.send_message(chat_id, "✅ Request Accepted!")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    if not check_join(chat_id): return
    if message.text == "🎯 Tasks": send_task(chat_id, 1)
    elif message.text == "🎁 Daily Bonus":
        now = time.time()
        if user['tasks_today'] < 2: bot.send_message(chat_id, "⚠️ Complete 2 full tasks first!")
        elif now - user['last_bonus'] < 86400: bot.send_message(chat_id, "❌ Already claimed!")
        else:
            user['balance'] += 2.0
            user['last_bonus'] = now
            bot.send_message(chat_id, "🎊 ৳2.00 Bonus Added!")
    elif message.text == "💰 Wallet":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Bkash", callback_data="method_Bkash"), 
                   types.InlineKeyboardButton("Nagad", callback_data="method_Nagad"))
        bot.send_message(chat_id, f"💰 Balance: ৳{round(user['balance'], 2)}", reply_markup=markup)
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 PROFILE\nName: {user['name']}\nID: {chat_id}\nBal: ৳{round(user['balance'], 2)}")
    elif message.text == "👫 Referral":
        bot.send_message(chat_id, f"👫 Link: https://t.me/TrustEarnCash_bot?start={chat_id}")
    elif message.text == "👑 Leaderboard":
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:5]
        lb = "👑 TOP 5\n"
        for i, (uid, uinfo) in enumerate(sorted_users, 1): lb += f"{i}. {uinfo['name']} - ৳{round(uinfo['balance'], 2)}\n"
        bot.send_message(chat_id, lb)

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"confirm_{task_no}"))
    text = f"💡 TASK: {task_no}/8\nView ad for 15s."
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(none_stop=True)
