import telebot
from telebot import types

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7364617700 # তোর আইডি

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0, 'name': message.from_user.first_name, 'referrals': 0}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, "Welcome to SuperFast Earning Bot! 🚀\nSelect an option below:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = user_data.get(chat_id, {'balance': 0, 'name': 'User'})

    if message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 **Name:** {user['name']}\n💰 **Balance:** ৳{user['balance']}\n👫 **Referrals:** {user['referrals']}")

    elif message.text == "💰 Wallet":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("bKash", callback_data="pay_bkash"),
                   types.InlineKeyboardButton("Nagad", callback_data="pay_nagad"))
        bot.send_message(chat_id, "Select your payment method:", reply_markup=markup)

    elif message.text == "👑 Leaderboard":
        bot.send_message(chat_id, "🏆 **Leaderboard Top 5**\n1. Iftekhar - ৳1000\n2. Coming Soon...")

# পেমেন্ট রিকোয়েস্ট হ্যান্ডেলার
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def payment(call):
    method = call.data.split("_")[1]
    msg = bot.send_message(call.message.chat.id, f"Please enter your {method} Number and Your Name:")
    bot.register_next_step_handler(msg, process_payment, method)

def process_payment(message, method):
    chat_id = message.chat.id
    user_info = message.text
    # অ্যাডমিনকে জানানো
    bot.send_message(ADMIN_ID, f"🔔 **New Withdrawal!**\nUser ID: {chat_id}\nMethod: {method}\nDetails: {user_info}")
    # ইউজারকে জানানো
    bot.send_message(chat_id, "✅ Request Submitted! Please wait 1-2 hours for your payment. Thank you! 🙏")

bot.polling()
                     
