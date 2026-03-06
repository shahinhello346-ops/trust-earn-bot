import telebot
from telebot import types

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
            'balance': 0.0, 'referrals': 0, 'name': name, 'no': len(user_list), 
            'banned': False, 'ref_by': None, 'tasks_done': 0, 'ref_paid': False
        }
    return user_data[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    if user['banned']: return

    # রেফারেল আইডি সেভ করা (টাকা এখনই দিবে না)
    text = message.text.split()
    if len(text) > 1 and text[1].isdigit():
        ref_id = int(text[1])
        if ref_id != chat_id and ref_id in user_data:
            user['ref_by'] = ref_id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"Welcome {user['name']}! 🚀\nComplete tasks to earn money.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)

    if call.data.startswith("confirm_"):
        task_no = int(call.data.split("_")[1])
        user['tasks_done'] = task_no
        
        # স্মার্ট রেফারেল: ৩ নম্বর কাজ শেষ করলে রেফারেল টাকা পাবে
        if task_no == 3 and user['ref_by'] and not user['ref_paid']:
            ref_id = user['ref_by']
            user_data[ref_id]['balance'] += 3.0
            user_data[ref_id]['referrals'] += 1
            user['ref_paid'] = True
            bot.send_message(ref_id, f"🎊 Referral Bonus! You earned ৳3.00 because your friend completed 3 tasks.")

        if task_no < 8:
            send_task(chat_id, task_no + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            bot.edit_message_text("🎊 Congratulations! 8 tasks completed. ৳0.92 added.", chat_id, call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if message.text == "🎯 Tasks": send_task(chat_id, 1)
    elif message.text == "💰 Wallet":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Bkash", callback_data="method_Bkash"), types.InlineKeyboardButton("Nagad", callback_data="method_Nagad"))
        bot.send_message(chat_id, "Choose Withdrawal Method:", reply_markup=markup)
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 Profile\n💰 Balance: ৳{round(user['balance'], 2)}\n👫 Invited: {user['referrals']}")
    elif message.text == "👫 Referral":
        link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"👫 Earn ৳3.00 per referral!\n(Friend must complete 3 tasks)\nLink: {link}")
    # বাকি বাটনগুলো (Leaderboard ইত্যাদি) আগের মতোই থাকবে

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"confirm_{task_no}"))
    text = f"💡 Task {task_no}/8\nStay on the ad for 15s or you will be BANNED!"
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

bot.polling(none_stop=True)
            
