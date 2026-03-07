import telebot
from telebot import types
from flask import Flask
from threading import Thread
import time
import random
from datetime import datetime

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
    today = datetime.now().strftime("%Y-%m-%d")
    if chat_id not in user_data:
        if chat_id not in user_list: user_list.append(chat_id)
        user_data[chat_id] = {
            'balance': 0.0, 'name': first_name, 'last_click': 0, 'tasks_today': 0, 
            'last_bonus': 0, 'spins_today': 0, 'last_spin_date': today, 'no': len(user_list)
        }
    
    if user_data[chat_id].get('last_spin_date') != today:
        user_data[chat_id]['spins_today'] = 0
        user_data[chat_id]['last_spin_date'] = today
        
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
        markup = types.InlineKeyboardMarkup(row_width=1)
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton(f"📢 Join @{ch}", url=f"https://t.me/{ch}"))
        markup.add(types.InlineKeyboardButton("✅ Joined - Click to Start", callback_data="check_status"))
        bot.send_message(chat_id, f"স্বাগতম {user['name']}!\nকাজ শুরু করতে নিচের ৩টি চ্যানেলে জয়েন করুন।", reply_markup=markup)
        return
    main_menu(chat_id)

def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "🎁 Daily Bonus", "🎡 Lucky Spin", "👑 Leaderboard", "👤 Profile")
    bot.send_message(chat_id, "Main Menu 🚀", reply_markup=markup)

# --- NEW: ADMIN ALL USERS LIST ---
@bot.message_handler(commands=['all_users'], func=lambda m: m.from_user.id == ADMIN_ID)
def list_all_users(message):
    if not user_list:
        bot.reply_to(message, "এখনো কোনো ইউজার জয়েন করেনি।")
        return
    msg = "👥 **ইউজার লিস্ট ও আইডি কোড:**\n\n"
    for uid in user_list:
        u = user_data[uid]
        msg += f"👤 {u['name']} | ID: `{uid}` | #No: {u['no']}\n"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['info'], func=lambda m: m.from_user.id == ADMIN_ID)
def check_info(message):
    try:
        _, uid = message.text.split()
        u = user_data[int(uid)]
        bot.reply_to(message, f"👤 ইউজার: {u['name']}\n🔢 মেম্বার নং: #{u['no']}\n💰 ব্যালেন্স: ৳{u['balance']}\n🎯 টাস্ক আজ: {u['tasks_today']}")
    except: bot.reply_to(message, "আইডি দিয়ে ট্রাই করো। উদাহরণ: /info 12345")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    if call.data == "check_status":
        if check_join(chat_id):
            bot.delete_message(chat_id, call.message.message_id)
            main_menu(chat_id)
        else: bot.answer_callback_query(call.id, "❌ জয়েন করেননি!", show_alert=True)
    elif call.data.startswith("confirm_"):
        now = time.time()
        if now - user['last_click'] < 15:
            bot.answer_callback_query(call.id, "⚠️ ১৫ সেকেন্ড অপেক্ষা করুন!")
            return
        user['last_click'] = now
        task_no = int(call.data.split("_")[1])
        if task_no < 8: send_task(chat_id, task_no + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            user['tasks_today'] += 1
            bot.edit_message_text("🎊 ৳০.৯২ যোগ হয়েছে।", chat_id, call.message.message_id)
    elif call.data.startswith("method_"):
        method = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("৳১০০", callback_data=f"amt_{method}_100"),
                   types.InlineKeyboardButton("৳২০০", callback_data=f"amt_{method}_200"))
        markup.add(types.InlineKeyboardButton("৳৫০০", callback_data=f"amt_{method}_500"),
                   types.InlineKeyboardButton("৳১০০০", callback_data=f"amt_{method}_1000"))
        bot.edit_message_text(f"উইথড্র পরিমাণ সিলেক্ট করুন:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("amt_"):
        _, method, amount = call.data.split("_")
        if user['balance'] < float(amount):
            bot.answer_callback_query(call.id, "❌ পর্যাপ্ত ব্যালেন্স নেই!", show_alert=True)
            return
        msg = bot.send_message(chat_id, f"আপনার {method} নাম্বার দিন:")
        bot.register_next_step_handler(msg, final_withdraw, method, amount)

def final_withdraw(message, method, amount):
    chat_id = message.chat.id
    user = get_user(chat_id)
    user['balance'] -= float(amount)
    bot.send_message(ADMIN_ID, f"🔔 পেমেন্ট রিকোয়েস্ট!\nID: `{chat_id}`\nমেথড: {method}\nপরিমাণ: ৳{amount}\nনাম্বার: {message.text}")
    bot.send_message(chat_id, "✅ রিকোয়েস্ট গৃহীত হয়েছে।")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    if not check_join(chat_id): return
    if message.text == "🎯 Tasks": send_task(chat_id, 1)
    elif message.text == "🎡 Lucky Spin":
        if user['spins_today'] >= 3:
            bot.send_message(chat_id, "❌ আজকের স্পিন শেষ!")
        else:
            res = ["❌", "😭", "৳১", "❌", "৳৫", "😭", "৳১০", "❌"]
            win = random.choice(res)
            user['spins_today'] += 1
            if "৳" in win:
                user['balance'] += int(win.replace("৳", ""))
                bot.send_message(chat_id, f"🎡 অভিনন্দন! জিতেছেন {win}!")
            else: bot.send_message(chat_id, f"🎡 {win} এবার কিছু পাননি।")
    elif message.text == "💰 Wallet":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Bkash", callback_data="method_Bkash"), 
                   types.InlineKeyboardButton("Nagad", callback_data="method_Nagad"))
        bot.send_message(chat_id, f"💰 ব্যালেন্স: ৳{round(user['balance'], 2)}", reply_markup=markup)
    elif message.text == "👑 Leaderboard":
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:20]
        lb = "👑 TOP 20\n"
        for i, (uid, uinfo) in enumerate(sorted_users, 1):
            lb += f"{i}. {uinfo['name']} - ৳{round(uinfo['balance'], 2)}\n"
        bot.send_message(chat_id, lb)
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 প্রোফাইল\n🏷 নাম: {user['name']}\n🔢 মেম্বার নং: #{user['no']}\n🆔 ID: `{chat_id}`\n💰 ব্যালেন্স: ৳{round(user['balance'], 2)}")
    elif message.text == "🎁 Daily Bonus":
        now = time.time()
        if user['tasks_today'] < 2: bot.send_message(chat_id, "⚠️ আগে ২টা টাস্ক শেষ করুন!")
        elif now - user['last_bonus'] < 86400: bot.send_message(chat_id, "❌ আজকের বোনাস নেওয়া শেষ!")
        else:
            user['balance'] += 2.0
            user['last_bonus'] = now
            bot.send_message(chat_id, "🎊 ৳২.০০ বোনাস যোগ হয়েছে!")

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"confirm_{task_no}"))
    text = f"💡 টাস্ক: {task_no}/8\nপুরষ্কার: ৳০.৯২"
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(none_stop=True)
