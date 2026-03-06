import telebot
from telebot import types
import time
import threading

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

user_data = {}

def get_user(chat_id, name="User"):
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0.0, 'referrals': 0, 'status': False, 'name': name}
    return user_data[chat_id]

# টাইমার ফাংশন যা বাটন আপডেট করবে
def start_button_timer(chat_id, message_id, task_no):
    for i in range(15, 0, -1):
        try:
            time.sleep(1)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f"⏳ Wait: {i}s...", url=AD_LINK))
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)
        except: return
    
    # ১৫ সেকেন্ড পর বাটন পাল্টে 'Confirm' হয়ে যাবে
    user_data[chat_id]['status'] = True
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"done_{task_no}"))
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    get_user(message.chat.id, message.from_user.first_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(message.chat.id, f"Welcome {message.from_user.first_name}! 🚀\nStart earning now!", reply_markup=markup)

def send_task(chat_id, task_no, message_id=None):
    user_data[chat_id]['status'] = False
    markup = types.InlineKeyboardMarkup()
    # প্রথম বাটনটা ক্লিক করলেই টাইমার শুরু হবে
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data=f"timer_{task_no}"))
    text = f"💡 **Task {task_no}/8**\nReward: ৳0.92\n\n১. View Ad বাটনে ক্লিক করো\n২. বাটনটা ১৫ সেকেন্ড কাউন্ট করবে\n৩. সময় শেষে Confirm বাটন আসবে"
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if "timer_" in call.data:
        task_no = call.data.split("_")[-1]
        # আলাদা থ্রেডে টাইমার চালানো যেন বট ফ্রীজ না হয়
        threading.Thread(target=start_button_timer, args=(chat_id, call.message.message_id, task_no)).start()
        bot.answer_callback_query(call.id, "Timer started! Stay on the ad.")
        
    elif "done_" in call.data:
        if user_data[chat_id]['status']:
            num = int(call.data.split("_")[-1])
            if num < 8:
                send_task(chat_id, num + 1, call.message.message_id)
            else:
                user_data[chat_id]['balance'] += 0.92
                bot.edit_message_text("🎊 Success! You earned ৳0.92", chat_id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "⚠️ Please wait for the timer!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    if message.text == "🎯 Tasks":
        send_task(message.chat.id, 1)
    elif message.text == "👤 Profile":
        user = get_user(message.chat.id)
        bot.send_message(message.chat.id, f"👤 Profile: {user['name']}\n💰 Balance: ৳{round(user['balance'], 2)}")

bot.polling(none_stop=True)
    
