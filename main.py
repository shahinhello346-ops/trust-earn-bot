import telebot
from telebot import types

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7364617700 
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0, 'ref': 0}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👤 প্রোফাইল")
    btn2 = types.KeyboardButton("🎯 কাজ করুন")
    btn3 = types.KeyboardButton("👫 রেফার করুন")
    btn4 = types.KeyboardButton("💸 টাকা তুলুন")
    btn5 = types.KeyboardButton("📢 চ্যানেল")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(chat_id, "স্বাগতম! নিচের মেনু থেকে অপশন বেছে নিন।", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0, 'ref': 0}

    if message.text == "👤 প্রোফাইল":
        user = user_data[chat_id]
        bot.send_message(chat_id, f"📌 **আপনার প্রোফাইল**\n\n🆔 আইডি: `{chat_id}`\n💰 ব্যালেন্স: {user['balance']} টাকা\n👫 রেফার: {user['ref']} জন", parse_mode="Markdown")
    
    elif message.text == "🎯 কাজ করুন":
        bot.send_message(chat_id, "নতুন কাজ আসছে... একটু অপেক্ষা করুন।")
    
    elif message.text == "👫 রেফার করুন":
        ref_link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"🔗 **আপনার রেফার লিঙ্ক:**\n{ref_link}\n\nপ্রতি রেফারে পাবেন ৫ টাকা!")

    elif message.text == "💸 টাকা তুলুন":
        bot.send_message(chat_id, "আপনার ব্যালেন্স নূন্যতম ১০০ টাকা হলে টাকা তুলতে পারবেন।")

bot.polling()
