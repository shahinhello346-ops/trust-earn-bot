import telebot
from telebot import types
import time

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

# অ্যাড লিংক
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
    first_name = message.from_user.first_name
    user = get_user(chat_id, first_name)
    
    # রেফারেল চেক
    text = message.text.split()
    if len(text) > 1 and text[1].isdigit():
        referrer_id = int(text[1])
        if referrer_id != chat_id and referrer_id in user_data:
            # এখানে তুই চাইলে রেফারারকে বোনাস দিতে পারিস
            pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome {first_name}! 🚀\nStart earning now!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if message.text == "🎯 Tasks":
        send_task(chat_id, 1)
    
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 **Profile Info**\n\n🆔 User ID: `{chat_id}`\n🔢 User No: #{user['uid']:03d}\n💰 Balance: ৳{round(user['balance'], 2)}\n👫 Invited: {user['referrals']}")
    
    elif message.text == "👫 Referral":
        # তোর কাস্টমাইজ রেফারেল লিংক এখানে তৈরি হচ্ছে
        ref_link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"👫 **Referral Program**\n\nShare your link to earn more!\n\nYour Link: {ref_link}\n\nPer Refer: ৳3.00")

    elif message.text == "👑 Leaderboard":
        # টপ ২০ ইউজারের নাম ও ব্যালেন্স আসবে
        top_users = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:20]
        lb_msg = "👑 **Top 20 Earners**\n\n"
        for i, (uid, data) in enumerate(top_users, 1):
            lb_msg += f"{i}. {data['name']} - ৳{round(data['balance'], 2)}\n"
        bot.send_message(chat_id, lb_msg)

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
        
        # টাইমার চেক (এখানেই আসল ফিক্স)
        if time.time() - user['last_click'] < 10:
            bot.answer_callback_query(call.id, "⚠️ Please wait 10 seconds!", show_alert=True)
            return
            
        num = int(call.data.split("_")[1])
        if num < 8:
            send_task(chat_id, num + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! You earned ৳0.92", chat_id, call.message.message_id)

bot.polling(none_stop=True)
    
