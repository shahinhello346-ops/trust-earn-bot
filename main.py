import telebot
from telebot import types
import time

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7364617700
AD_LINK = 'Https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c' 

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        args = message.text.split()
        referrer = None
        if len(args) > 1 and args[1].isdigit():
            referrer = int(args[1])
            if referrer in user_data:
                user_data[referrer]['balance'] += 3.0
                user_data[referrer]['referrals'] += 1
                bot.send_message(referrer, f"👫 Referral Bonus! You earned ৳3.0")
        
        user_data[chat_id] = {'balance': 1.0 if referrer else 0.0, 'name': message.from_user.first_name, 'referrals': 0, 'last_ad_click': 0, 'ad_status': False}
        if referrer: bot.send_message(chat_id, "🎁 You earned ৳1.0 Joining Bonus!")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome {message.from_user.first_name}! 🚀\nStart earning now!", reply_markup=markup)

def send_task(chat_id, task_no, message_id=None):
    user_data[chat_id]['ad_status'] = False 
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
    
    if call.data == "clicked_ad":
        user_data[chat_id]['last_ad_click'] = time.time()
        user_data[chat_id]['ad_status'] = True
        bot.answer_callback_query(call.id, "Timer Started! Wait 10 seconds.")
        bot.send_message(chat_id, "⏳ Timer started! Please wait 10 seconds on the ad page before clicking Confirm.")
        
    elif call.data.startswith("task_"):
        if not user_data[chat_id].get('ad_status'):
            bot.answer_callback_query(call.id, "❌ Error: Click 'View Ad' first!", show_alert=True)
            return
        
        elapsed = time.time() - user_data[chat_id].get('last_ad_click', 0)
        if elapsed < 10:
            remaining = int(10 - elapsed)
            bot.answer_callback_query(call.id, f"⚠️ Please wait {remaining} more seconds!", show_alert=True)
            return
            
        num = int(call.data.split("_")[1])
        if num < 8:
            send_task(chat_id, num + 1, call.message.message_id)
        else:
            user_data[chat_id]['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! You earned ৳0.92", chat_id, call.message.message_id)

    elif call.data.startswith("pay_"):
        method = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("৳100", callback_data=f"amt_{method}_100"),
                   types.InlineKeyboardButton("৳250", callback_data=f"amt_{method}_250"),
                   types.InlineKeyboardButton("৳500", callback_data=f"amt_{method}_500"),
                   types.InlineKeyboardButton("৳1000", callback_data=f"amt_{method}_1000"))
        bot.edit_message_text(f"Select Amount ({method}):", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("amt_"):
        _, method, amount = call.data.split("_")
        msg = bot.send_message(chat_id, f"Withdraw ৳{amount} ({method}).\nEnter your Number:")
        bot.register_next_step_handler(msg, process_payment, method, amount)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    if message.text == "🎯 Tasks":
        send_task(chat_id, 1)
    elif message.text == "👤 Profile":
        user = user_data.get(chat_id, {'balance': 0, 'referrals': 0})
        bot.send_message(chat_id, f"👤 **Profile Info**\n💰 Balance: ৳{round(user['balance'], 2)}\n👫 Invited: {user['referrals']}")
    elif message.text == "👑 Leaderboard":
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:30]
        lb_text = "🏆 **Leaderboard Top 30**\n\n"
        for i, (uid, uinfo) in enumerate(sorted_users, 1):
            lb_text += f"{i}. {uinfo['name']} - ৳{round(uinfo['balance'], 2)}\n"
        bot.send_message(chat_id, lb_text)
    elif message.text == "💰 Wallet":
        if user_data[chat_id]['balance'] < 100:
            bot.send_message(chat_id, f"❌ Min withdraw ৳100. Balance: ৳{round(user_data[chat_id]['balance'], 2)}")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("bKash", callback_data="pay_bkash"),
                       types.InlineKeyboardButton("Nagad", callback_data="pay_nagad"))
            bot.send_message(chat_id, "Choose Payment Method:", reply_markup=markup)

def process_payment(message, method, amount):
    bot.send_message(ADMIN_ID, f"🔔 **New Request!**\nAmount: ৳{amount}\nMethod: {method}\nInfo: {message.text}")
    bot.send_message(message.chat.id, "✅ Request Submitted! Please wait 1-2 hours.")

bot.polling()
            
