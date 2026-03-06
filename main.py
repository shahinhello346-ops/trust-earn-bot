import telebot
from telebot import types
import time

# তোর বটের টোকেন
API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

# তোর এডমিন আইডি
ADMIN_ID = 7364617700
# নতুন স্মার্টলিঙ্ক
AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0.0, 'name': message.from_user.first_name, 'referrals': 0, 'last_ad_click': 0, 'ad_status': False}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome {message.from_user.first_name}! 🚀\nStart earning by viewing ads!", reply_markup=markup)

def send_task(chat_id, task_no, message_id=None):
    user_data[chat_id]['ad_status'] = False 
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data="clicked_ad"))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"task_{task_no}"),
               types.InlineKeyboardButton("Skip ⏭️", callback_data=f"skip_{task_no}"))
    msg_text = f"💡 **Task {task_no}/8**\n\n1. Click 'View Ad'\n2. Stay for 10 seconds\n3. Press 'Confirm'"
    if message_id:
        try: bot.edit_message_text(msg_text, chat_id, message_id, reply_markup=markup)
        except: bot.send_message(chat_id, msg_text, reply_markup=markup)
    else:
        bot.send_message(chat_id, msg_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_all(call):
    chat_id = call.message.chat.id
    if call.data == "clicked_ad":
        user_data[chat_id]['last_ad_click'] = time.time()
        user_data[chat_id]['ad_status'] = True
        bot.answer_callback_query(call.id, "Timer Started!")
        bot.send_message(chat_id, "⏳ Timer started! Please wait 10 seconds.")
    
    elif call.data.startswith("task_"):
        if not user_data[chat_id].get('ad_status'):
            bot.answer_callback_query(call.id, "❌ Click 'View Ad' first!", show_alert=True)
            return
        
        elapsed = time.time() - user_data[chat_id].get('last_ad_click', 0)
        if elapsed < 10:
            bot.answer_callback_query(call.id, f"⚠️ Wait {int(10-elapsed)}s more!", show_alert=True)
            return
            
        num = int(call.data.split("_")[1])
        if num < 8:
            send_task(chat_id, num + 1, call.message.message_id)
        else:
            user_data[chat_id]['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! You earned ৳0.92", chat_id, call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    if message.text == "🎯 Tasks":
        send_task(chat_id, 1)
    elif message.text == "👤 Profile":
        user = user_data.get(chat_id, {'balance': 0, 'referrals': 0})
        bot.send_message(chat_id, f"👤 Profile: {user['name']}\n💰 Balance: ৳{round(user['balance'], 2)}")
    elif message.text == "💰 Wallet":
        if user_data[chat_id]['balance'] < 100:
            bot.send_message(chat_id, f"❌ Min withdraw ৳100. Current: ৳{round(user_data[chat_id]['balance'], 2)}")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("bKash", callback_data="pay_bkash"),
                       types.InlineKeyboardButton("Nagad", callback_data="pay_nagad"))
            bot.send_message(chat_id, "Choose Method:", reply_markup=markup)

bot.polling(none_stop=True)
    
