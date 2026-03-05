import telebot
from telebot import types

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7364617700
AD_LINK = 'https://duepose.com/xyvx9nv8i?key=e3df24b13a4d3489c4e3c19d7203fb6f'

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0, 'name': message.from_user.first_name, 'referrals': 0, 'ad_clicked': False}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome {message.from_user.first_name}! 🚀\nStart earning now!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    text = message.text
    if chat_id not in user_data: user_data[chat_id] = {'balance': 0, 'name': message.from_user.first_name, 'referrals': 0, 'ad_clicked': False}

    if text == "🎯 Tasks":
        user_data[chat_id]['ad_clicked'] = False
        send_task(chat_id, 1)
        
    elif text == "👤 Profile":
        user = user_data[chat_id]
        bot.send_message(chat_id, f"👤 **Profile Info**\n\n💰 Balance: ৳{round(user['balance'], 2)}\n👫 Invited: {user['referrals']}")

    elif text == "💰 Wallet":
        if user_data[chat_id]['balance'] < 100:
            bot.send_message(chat_id, f"❌ Min withdraw ৳100.\nYour balance: ৳{round(user_data[chat_id]['balance'], 2)}")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("bKash", callback_data="pay_bkash"),
                       types.InlineKeyboardButton("Nagad", callback_data="pay_nagad"))
            bot.send_message(chat_id, "Choose Payment Method:", reply_markup=markup)

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data="clicked_ad"),
               types.InlineKeyboardButton("Confirm ✅", callback_data=f"task_{task_no}"))
    
    msg_text = f"💡 **Task {task_no}/8**\nReward: +৳0.92\n\n(Click 'View Ad' first, then 'Confirm')"
    
    if message_id:
        bot.edit_message_text(msg_text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, msg_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_all(call):
    chat_id = call.message.chat.id
    if call.data == "clicked_ad":
        user_data[chat_id]['ad_clicked'] = True
        bot.answer_callback_query(call.id, "Ad tracked! Now press Confirm.")
    
    elif call.data.startswith("task_"):
        if not user_data[chat_id].get('ad_clicked'):
            bot.answer_callback_query(call.id, "❌ Error: Click 'View Ad' first!", show_alert=True)
            return
        
        num = int(call.data.split("_")[1])
        user_data[chat_id]['ad_clicked'] = False
        if num < 8:
            send_task(chat_id, num + 1, call.message.message_id)
        else:
            user_data[chat_id]['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! You earned ৳0.92!", chat_id, call.message.message_id)

    elif call.data.startswith("pay_"):
        method = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("৳100", callback_data=f"amt_{method}_100"),
                   types.InlineKeyboardButton("৳200", callback_data=f"amt_{method}_200"),
                   types.InlineKeyboardButton("৳500", callback_data=f"amt_{method}_500"))
        bot.edit_message_text(f"Select Amount ({method}):", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("amt_"):
        _, method, amount = call.data.split("_")
        msg = bot.send_message(chat_id, f"Selected: ৳{amount} ({method}).\nEnter your Number:")
        bot.register_next_step_handler(msg, process_payment, method, amount)

def process_payment(message, method, amount):
    if message.text in ["🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile"]:
        bot.send_message(message.chat.id, "❌ Cancelled.")
        return
    bot.send_message(ADMIN_ID, f"🔔 **New Request!**\nAmount: ৳{amount}\nMethod: {method}\nInfo: {message.text}")
    bot.send_message(message.chat.id, "✅ Request submitted!")

bot.polling()
