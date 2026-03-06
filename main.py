import telebot
from telebot import types

# তোর টোকেন এবং এডমিন আইডি
API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 7364617700

AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c'

user_data = {}
user_list = []

def get_user(chat_id, name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list: user_list.append(chat_id)
        user_data[chat_id] = {
            'balance': 0.0, 'referrals': 0, 'name': name, 'no': len(user_list), 'banned': False
        }
    return user_data[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.chat.id, message.from_user.first_name)
    if user['banned']:
        bot.send_message(message.chat.id, "❌ Your account has been banned for violating rules!")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(message.chat.id, f"Welcome {user['name']}! 🚀\nWork honestly and earn daily rewards.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    if user['banned']: return

    if message.text == "🎯 Tasks":
        send_task(chat_id, 1)
    
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 **Your Profile**\n🆔 UID: `{chat_id}`\n🔢 User No: #{user['no']:03d}\n💰 Balance: ৳{round(user['balance'], 2)}\n👫 Invited: {user['referrals']}")
    
    elif message.text == "👫 Referral":
        link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"👫 Earn ৳3.00 per successful referral!\nYour Link:\n{link}")

    elif message.text == "👑 Leaderboard":
        top = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
        lb = "👑 **Top 10 Earners**\n\n"
        for i, (uid, data) in enumerate(top, 1):
            lb += f"{i}. {data['name']} - ৳{round(data['balance'], 2)}\n"
        bot.send_message(chat_id, lb)

    elif message.text == "💰 Wallet":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Bkash", callback_data="method_Bkash"))
        markup.add(types.InlineKeyboardButton("Nagad", callback_data="method_Nagad"))
        bot.send_message(chat_id, "💰 Choose Withdrawal Method:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)

    if call.data.startswith("method_"):
        method = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup()
        for amt in [100, 250, 500, 1000]:
            markup.add(types.InlineKeyboardButton(f"৳{amt}", callback_data=f"withdraw_{method}_{amt}"))
        bot.edit_message_text(f"How much do you want to withdraw via {method}?", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("withdraw_"):
        _, method, amt = call.data.split("_")
        if user['balance'] < float(amt):
            bot.answer_callback_query(call.id, "❌ Insufficient balance!", show_alert=True)
        else:
            msg = bot.send_message(chat_id, f"✅ Enter your {method} number to receive ৳{amt}:")
            bot.register_next_step_handler(msg, process_withdraw, method, amt)

    elif call.data.startswith("confirm_"):
        task_no = int(call.data.split("_")[1])
        if task_no < 8:
            send_task(chat_id, task_no + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! 8 tasks completed. ৳0.92 added to balance.", chat_id, call.message.message_id)
        
        # Report to Admin
        bot.send_message(ADMIN_ID, f"🔔 **Report:** {user['name']} (ID: `{chat_id}`) confirmed task. Check if they stayed for 15s.")

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"confirm_{task_no}"))
    text = f"💡 **Task {task_no}/8**\nReward: ৳0.92\n\n⚠️ **WARNING:** You MUST stay on the ad page for 15 seconds. If you cheat, you will be BANNED and will not get paid!"
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

def process_withdraw(message, method, amt):
    number = message.text
    bot.send_message(message.chat.id, "✅ Request submitted! Please wait 1-2 hours for payment.")
    bot.send_message(ADMIN_ID, f"💰 **NEW WITHDRAW REQUEST!**\nName: {message.from_user.first_name}\nID: `{message.chat.id}`\nMethod: {method}\nAmount: ৳{amt}\nNumber: `{number}`")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "👨‍✈️ Admin Commands:\nBan: /ban [UID]\nUnban: /unban [UID]")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.chat.id == ADMIN_ID:
        try:
            uid = int(message.text.split()[1])
            user_data[uid]['banned'] = True
            bot.send_message(ADMIN_ID, f"✅ User {uid} has been BANNED!")
        except: bot.send_message(ADMIN_ID, "Use: /ban [UID]")

bot.polling(none_stop=True)
        
