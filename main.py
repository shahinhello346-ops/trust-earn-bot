import telebot
from telebot import types
import time

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

user_data = {}
user_list = []

def get_user(chat_id, first_name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list:
            user_list.append(chat_id)
        user_data[chat_id] = {
            'balance': 0.0, 
            'referrals': 0, 
            'last_click': 0, 
            'status': False,
            'name': first_name,
            'uid': len(user_list)
        }
    return user_data[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    # রেফারেল বোনাস ৳৩ (যে রেফার করবে তার জন্য)
    text = message.text.split()
    if len(text) > 1 and text[1].isdigit():
        ref_id = int(text[1])
        if ref_id != chat_id and ref_id in user_data:
            user_data[ref_id]['balance'] += 3.0
            user_data[ref_id]['referrals'] += 1
            bot.send_message(ref_id, f"🎊 Success! You earned ৳3.00 for inviting {user['name']}")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome {user['name']}! 🚀\nStart earning now!", reply_markup=markup)

def send_task(chat_id, task_no, message_id=None):
    user = get_user(chat_id)
    user['status'] = False 
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data="clicked_ad"))
    
    # শুরুতে কনফার্ম বাটন দেখাবে না, শুধু ইনস্ট্রাকশন
    msg_text = f"💡 **Task {task_no}/8**\nReward: ৳0.92\n\n1. Click 'View Ad'\n2. Wait for the timer to finish\n3. Confirm button will appear after 15s"
    
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
        bot.answer_callback_query(call.id, "Timer Started! Stay 15s.")
        
        # এখানে একটা ম্যাজিক—টাইমার কাউন্টডাউন মেসেজ
        for i in range(15, 0, -1):
            try:
                bot.edit_message_text(f"⏳ Stay on the Ad page: {i} seconds left...", chat_id, call.message.message_id)
                time.sleep(1)
            except: break
            
        # সময় শেষ হলে কনফার্ম বাটন পাঠিয়ে দেওয়া
        markup = types.InlineKeyboardMarkup()
        # এখানে task_no টা ধরে রাখার জন্য একটা বুদ্ধি খাটাতে হবে, আপাতত ১ দিয়ে রাখছি
        task_num = 1 
        markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"task_{task_num}"))
        bot.edit_message_text("✅ 15s Finished! Now you can confirm.", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("task_"):
        if not user['status']:
            bot.answer_callback_query(call.id, "❌ Click 'View Ad' first!", show_alert=True)
            return
            
        num = int(call.data.split("_")[1])
        if num < 8:
            send_task(chat_id, num + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! You earned ৳0.92", chat_id, call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    if message.text == "🎯 Tasks":
        send_task(message.chat.id, 1)
    elif message.text == "👤 Profile":
        user = get_user(message.chat.id)
        bot.send_message(message.chat.id, f"👤 Profile: {user['name']}\n🆔 UID: {message.chat.id}\n💰 Balance: ৳{round(user['balance'], 2)}")
    elif message.text == "👫 Referral":
        link = f"https://t.me/TrustEarnCash_bot?start={message.chat.id}"
        bot.send_message(message.chat.id, f"👫 Invite friends and earn ৳3.00!\n\nLink: {link}")

bot.polling(none_stop=True)
