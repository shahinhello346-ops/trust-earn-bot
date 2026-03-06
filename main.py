import telebot
from telebot import types
import time

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7364617700
AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

# ডাটা সেভ রাখার জন্য
user_data = {}
user_list = [] # ইউজার কত নম্বর সেটা মাপার জন্য

def get_user(chat_id):
    if chat_id not in user_data:
        if chat_id not in user_list:
            user_list.append(chat_id)
        user_data[chat_id] = {
            'balance': 0.0, 
            'referrals': 0, 
            'last_click': 0, 
            'status': False,
            'uid': len(user_list) # ইউজারের সিরিয়াল নম্বর
        }
    return user_data[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    get_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(message.chat.id, f"Welcome {message.from_user.first_name}! 🚀\nStart earning now!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    text = message.text

    if text == "🎯 Tasks":
        send_task(chat_id, 1)
    elif text == "👤 Profile":
        # প্রোফাইলে ইউজার আইডি এবং সিরিয়াল নম্বর যোগ করা হয়েছে
        bot.send_message(chat_id, f"👤 **Profile Info**\n\n🆔 User ID: `{chat_id}`\n🔢 User No: #{user['uid']:03d}\n💰 Balance: ৳{round(user['balance'], 2)}\n👫 Invited: {user['referrals']}")
    elif text == "👑 Leaderboard":
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:30]
        lb_text = "🏆 **Leaderboard Top 30**\n\n"
        for i, (uid, uinfo) in enumerate(sorted_users, 1):
            lb_text += f"{i}. {uinfo['name'] if 'name' in uinfo else 'User'} - ৳{round(uinfo['balance'], 2)}\n"
        bot.send_message(chat_id, lb_text)
    elif text == "💰 Wallet":
        if user['balance'] < 100:
            bot.send_message(chat_id, f"❌ Min withdraw ৳100. Your balance: ৳{round(user['balance'], 2)}")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("bKash", callback_data="pay_bkash"),
                       types.InlineKeyboardButton("Nagad", callback_data="pay_nagad"))
            bot.send_message(chat_id, "Choose Payment Method:", reply_markup=markup)

def send_task(chat_id, task_no, message_id=None):
    user = get_user(chat_id)
    user['status'] = False 
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data="clicked_ad"))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"task_{task_no}"),
               types.InlineKeyboardButton("Skip ⏭️", callback_data=f"skip_{task_no}"))
    msg_text = f"💡 **Task {task_no}/8**\nReward: ৳0.92\n\n1. Click 'View Ad'\n2. Stay for 10 seconds\n3. Press 'Confirm'"
    if message_id:
        try: bot.edit_message_text(msg_text, chat_id, message_id, reply_markup=markup)
        except: bot.send_message(chat_id, msg_text, reply_markup=markup)
    else:
        bot.send_message(chat_id, msg_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_all(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    
    if call.data == "clicked_ad":
        user['last_click'] = time.time()
        user['status'] = True
        bot.answer_callback_query(call.id, "Timer Started! Wait 10 seconds.")
    elif call.data.startswith("task_"):
        if not user['status']:
            bot.answer_callback_query(call.id, "❌ Error: Click 'View Ad' first!", show_alert=True)
            return
        
        elapsed = time.time() - user['last_click']
        if elapsed < 10:
            bot.answer_callback_query(call.id, f"⚠️ Wait {int(10-elapsed)}s more!", show_alert=True)
            return
            
        num = int(call.data.split("_")[1])
        if num < 8:
            send_task(chat_id, num + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! You earned ৳0.92", chat_id, call.message.message_id)

bot.polling(none_stop=True)
    
