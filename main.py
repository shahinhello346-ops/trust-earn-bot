import telebot
from telebot import types

# তোর বটের টোকেন
API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

# তোর আইডি এখানে বসিয়ে দিয়েছি
ADMIN_ID = 7364617700 

user_language = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn_bn = types.InlineKeyboardButton("🇧🇩 বাংলা", callback_data='lang_bn')
    btn_en = types.InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')
    markup.add(btn_bn, btn_en)
    
    bot.send_message(message.chat.id, "Please select your language / ভাষা নির্বাচন করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    chat_id = call.message.chat.id
    if call.data == 'lang_bn':
        user_language[chat_id] = 'bn'
        msg = "স্বাগতম! আপনি বাংলা ভাষা বেছে নিয়েছেন। 🇧🇩\nএখন থেকে আমি আপনার সাথে বাংলায় কথা বলব।"
    else:
        user_language[chat_id] = 'en'
        msg = "Welcome! You have selected English. 🇺🇸\nFrom now on, I will speak with you in English."
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=msg)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "হ্যালো বস! আপনি অ্যাডমিন প্যানেলে ঢুকেছেন। আপনার সব কন্ট্রোল এখানে। 😎")
    else:
        bot.reply_to(message, "দুঃখিত, এই কমান্ডটি শুধুমাত্র অ্যাডমিনের জন্য।")

bot.polling()
        
