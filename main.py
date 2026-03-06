import telebot
from telebot import types
import time
import threading

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

# তোর এডমিন আইডি (এটা ঠিক আছে তো?)
ADMIN_ID = 7364617700
AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

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

# বাটন টাইমার ফাংশন
def button_timer(chat_id, message_id, task_no):
    for i in range(15, 0, -1):
        try:
            time.sleep(1)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f"⏳ Waiting: {i}s", url=AD_LINK))
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)
        except: return
    
    user_data[chat_id]['status'] = True
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Confirm ✅ (Claim ৳0.92)", callback_data=f"done_{task_no}"))
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    # রেফারেল সিস্টেম (৩ টাকা বোনাস)
    text = message.text.split()
    if len(text) > 1 and text[1].isdigit():
        ref_id = int(text[1])
        if ref_id != chat_id and ref_id in user_data:
            user_data[ref_id]['balance'] += 3.0
            user_data[ref_id]['referrals'] += 1
            bot.send_message(ref_id, f"🎊 New Referral! You earned ৳3.00 for inviting {user['name']}")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome {user['name']}! 🚀\nStart earning now!", reply_markup=markup)

# এডমিন প্যানেল কমান্ড
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        total_users = len(user_list)
        msg = f"👨‍✈️ **Admin Control Panel**\n\n👥 Total Users: {total_users}\n\n"
        msg += "ইউজারদের লিস্ট দেখতে '👤 User List' এ ক্লিক করো।"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("👤 User List", "📊 Stats", "🔙 Back to Home")
        bot.send_message(ADMIN_ID, msg, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Sorry, this command is only for Admin.")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if message.text == "🎯 Tasks":
        send_task(chat_id, 1)
    elif message.text == "👤 Profile":
        # এখানে UID আর User No যোগ করা হয়েছে
        bot.send_message(chat_id, f"👤 **Profile Info**\n\n🆔 UID: `{chat_id}`\n🔢 User No: #{user['no']:03d}\n💰 Balance: ৳{round(user['balance'], 2)}\n👫 Invited: {user['referrals']}")
    elif message.text == "👫 Referral":
        link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"👫 **Referral Program**\n\nInvite friends and earn ৳3.00 per person!\n\nLink: {link}")
    
    # এডমিন ফাংশনালিটি
    elif message.text == "👤 User List" and chat_id == ADMIN_ID:
        user_list_msg = "📋 **User Database:**\n\n"
        for uid, data in user_data.items():
            user_list_msg += f"Name: {data['name']}\nID: `{uid}`\nBal: ৳{data['balance']}\nRef: {data['referrals']}\n---\n"
        bot.send_message(ADMIN_ID, user_list_msg)
    elif message.text == "🔙 Back to Home":
        start(message)

def send_task(chat_id, task_no, message_id=None):
    user_data[chat_id]['status'] = False
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data=f"start_{task_no}"))
    text = f"💡 **Task {task_no}/8**\nReward: ৳0.92\n\n১. 'View Ad' এ ক্লিক কর।\n২. ১৫ সেকেন্ড বাটনটি কাউন্ট করবে।\n৩. সময় শেষে Confirm বাটন আসবে।"
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    chat_id = call.message.chat.id
    if "start_" in call.data:
        task_no = call.data.split("_")[-1]
        bot.answer_callback_query(call.id, "Timer started!")
        threading.Thread(target=button_timer, args=(chat_id, call.message.message_id, task_no)).start()
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
