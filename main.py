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
    referrer_id = None
    if len(message.text.split()) > 1:
        referrer_id = message.text.split()[1]
        
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0, 'name': message.from_user.first_name, 'referrals': 0}
        if referrer_id and int(referrer_id) in user_data and int(referrer_id) != chat_id:
            user_data[int(referrer_id)]['balance'] += 3
            user_data[int(referrer_id)]['referrals'] += 1
            user_data[chat_id]['balance'] += 1 
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    if chat_id == ADMIN_ID:
        markup.add("📊 Admin Stats")
        
    bot.send_message(chat_id, f"Welcome {message.from_user.first_name}! 🚀\nStart earning Stars now!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    text = message.text
    if chat_id not in user_data: user_data[chat_id] = {'balance': 0, 'name': message.from_user.first_name, 'referrals': 0}

    if text == "🎯 Tasks":
        send_task(chat_id, 1)
        
    elif text == "👫 Referral":
        ref_link = f"https://t.me/StarsMakeBot?start={chat_id}"
        msg_text = (f"🎁 **Referral Program**\n\n"
                    f"Get +৳3 for every friend you invite!\n"
                    f"Your friend gets +৳1 for joining.\n\n"
                    f"🔗 **Your Referral Link:**\n`{ref_link}`\n\n"
                    f"Total Invited: {user_data[chat_id]['referrals']}")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Share with Friends ↗️", url=f"https://t.me/share/url?url={ref_link}"))
        bot.send_message(chat_id, msg_text, reply_markup=markup, parse_mode="Markdown")

    elif text == "👑 Leaderboard":
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:30]
        lb_text = "🏆 **Top 30 Leaderboard**\n\n"
        for i, (uid, data) in enumerate(sorted_users, 1):
            lb_text += f"{i}. {data['name']} - ৳{round(data['balance'], 2)}\n"
        bot.send_message(chat_id, lb_text)

    elif text == "📊 Admin Stats" and chat_id == ADMIN_ID:
        bot.send_message(chat_id, f"📊 **Bot Statistics**\n\nTotal Users: {len(user_data)}\nStatus: Online ✅")

    elif text == "💰 Wallet":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("bKash", callback_data="pay_bkash"),
                   types.InlineKeyboardButton("Nagad", callback_data="pay_nagad"))
        bot.send_message(chat_id, "Choose your payment method:", reply_markup=markup)

    elif text == "👤 Profile":
        user = user_data[chat_id]
        bot.send_message(chat_id, f"👤 **Profile**\n\nName: {user['name']}\nBalance: ৳{round(user['balance'], 2)}\nInvited: {user['referrals']}")

def send_task(chat_id, task_no):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK),
               types.InlineKeyboardButton("Confirm ✅", callback_data=f"task_{task_no}"))
    markup.add(types.InlineKeyboardButton("Skip ⏩", callback_data=f"skip_{task_no}"))
    bot.send_message(chat_id, f"💡 **Task {task_no}/8**\n\nClick 'View Ad', wait 10s, then press 'Confirm'.\n\nReward: +৳0.92", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_all(call):
    chat_id = call.message.chat.id
    if call.data.startswith("task_"):
        num = int(call.data.split("_")[1])
        if num < 8:
            bot.edit_message_text(f"✅ Task {num} completed!", chat_id, call.message.message_id)
            send_task(chat_id, num + 1)
        else:
            user_data[chat_id]['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! You earned ৳0.92!", chat_id, call.message.message_id)
    elif call.data.startswith("pay_"):
        method = call.data.split("_")[1]
        msg = bot.send_message(chat_id, f"Enter your {method} Number and Name:")
        bot.register_next_step_handler(msg, process_payment, method)

def process_payment(message, method):
    if message.text in ["🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile"]:
        bot.send_message(message.chat.id, "❌ Action Cancelled.")
        return
    bot.send_message(ADMIN_ID, f"🔔 **Withdrawal!**\nMethod: {method}\nInfo: {message.text}")
    bot.send_message(message.chat.id, "✅ Submitted! Wait 1-2 hours for payment.")

bot.polling()
            
