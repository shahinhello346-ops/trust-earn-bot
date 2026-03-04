import telebot

# তোর বটের টোকেন
API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "টাস্ট আর্ন বটে আপনাকে স্বাগতম! 💸\nএখানে ছোট ছোট কাজ করে টাকা আয় করুন।")

bot.polling()
