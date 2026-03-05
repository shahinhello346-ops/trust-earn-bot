import telebot
from telebot import types

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7364617700 
user_data = {} # এখানে সবার ব্যালেন্স সেভ থাকবে

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💰 আমার ব্যালেন্স")
    btn2 = types.KeyboardButton("🎯 কাজ করুন")
    btn3 = types.KeyboardButton("📢 আমাদের চ্যানেল")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(chat_id, "স্বাগতম! নিচের বাটনগুলো ব্যবহার করে কাজ শুরু করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {'balance': 0}

    if message.text == "💰 আমার ব্যালেন্স":
        balance = user_data[chat_id]['balance']
        bot.send_message(chat_id, f"আপনার বর্তমান ব্যালেন্স: {balance} টাকা")
    
    elif message.text == "🎯 কাজ করুন":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("ভিজিট করুন", url="https://google.com") # এখানে তোর লিঙ্ক দিবি
        markup.add(btn)
        bot.send_message(chat_id, "নিচের লিঙ্কে গিয়ে ১ মিনিট অপেক্ষা করুন। কাজ শেষ হলে ১০ টাকা পাবেন।", reply_markup=markup)
        # পরে আমরা এটা অটোমেটিক ব্যালেন্স যোগ হওয়ার সিস্টেম করব
    
    elif message.text == "📢 আমাদের চ্যানেল":
        bot.send_message(chat_id, "আমাদের অফিশিয়াল চ্যানেলে জয়েন করুন: @YourChannelLink")

bot.polling()
    
