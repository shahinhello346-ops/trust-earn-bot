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
            'last_bonus': 0, 'spins_today': 0, 'last_spin_date': today, 'no': len(user_list), 'referrals': 0
        }
    if user_data[chat_id].get('last_spin_date') != today:
        user_data[chat_id]['spins_today'] = 0
        user_data[chat_id]['last_spin_date'] = today
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
    first_name = message.from_user.first_name
    
    # রেফারেল চেক
    if chat_id not in user_data and " " in message.text:
        try:
            referrer_id = int(message.text.split()[1])
            if referrer_id != chat_id and referrer_id in user_data:
                user_data[referrer_id]['balance'] += 1.0 # রেফার বোনাস ১ টাকা
                user_data[referrer_id]['referrals'] += 1
                bot.send_message(referrer_id, f"🎊 অভিনন্দন! আপনার লিঙ্কে একজন নতুন ইউজার জয়েন করেছে। আপনি ৳১.০০ বোনাস পেয়েছেন।")
        except: pass

    user = get_user(chat_id, first_name)
    if not check_join(chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton(f"📢 Join @{ch}", url=f"https://t.me/{ch}"))
        markup.add(types.InlineKeyboardButton("✅ Joined - Click to Start", callback_data="check_status"))
        bot.send_message(chat_id, f"স্বাগতম {user['name']}!\nকাজ শুরু করতে ৩টি চ্যানেলে জয়েন করুন।", reply_markup=markup)
        return
    main_menu(chat_id)

def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # এখানে রেফার বাটন যোগ করা হয়েছে
    markup.add("🎯 Tasks", "💰 Wallet", "🎁 Daily Bonus", "🎡 Lucky Spin", "👫 Refer", "👑 Leaderboard", "👤 Profile")
    bot.send_message(chat_id, "Main Menu 🚀\nনিচের বাটনগুলো ব্যবহার করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    if not check_join(chat_id): return

    if message.text == "🎯 Tasks":
        send_task(chat_id, 1)
    elif message.text == "👫 Refer":
        ref_link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"👫 **আপনার রেফারেল লিঙ্ক:**\n`{ref_link}`\n\nপ্রতিটি সফল রেফারে পাবেন **৳১.০০** বোনাস! বন্ধুদের ইনভাইট করুন আর আয় বাড়ান।", parse_mode="Markdown")
    elif message.text == "🎡 Lucky Spin":
        if user['spins_today'] >= 3:
            bot.send_message(chat_id, "❌ আজকের স্পিন শেষ! রাত ১২টার পর আবার পাবেন।")
        else:
            res = ["❌", "😭", "৳১", "❌", "৳৫", "😭", "৳১০", "❌"]
            win = random.choice(res)
            user['spins_today'] += 1
            if "৳" in win:
                user['balance'] += int(win.replace("৳", ""))
                bot.send_message(chat_id, f"🎡 অভিনন্দন! আপনি জিতেছেন {win}!")
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
        bot.send_message(chat_id, f"👤 প্রোফাইল\n🏷 নাম: {user['name']}\n🔢 মেম্বার নং: #{user['no']}\n🆔 ID: `{chat_id}`\n👫 রেফার: {user['referrals']}\n💰 ব্যালেন্স: ৳{round(user['balance'], 2)}")
    elif message.text == "🎁 Daily Bonus":
        now = time.time()
        if user['tasks_today'] < 2: bot.send_message(chat_id, "⚠️ আগে ২টা টাস্ক শেষ করুন!")
        elif now - user['last_bonus'] < 86400: bot.send_message(chat_id, "❌ আজকের বোনাস নেওয়া শেষ!")
        else:
            user['balance'] += 2.0
            user['last_bonus'] = now
            bot.send_message(chat_id, "🎊 ৳২.০০ বোনাস যোগ হয়েছে!")

# Admin commands, callback logic, and send_task remains the same...
# [বাকি অংশ আগের কোডের মতোই থাকবে]
