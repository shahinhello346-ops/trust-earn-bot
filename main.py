import telebot
import time
from flask import Flask
from threading import Thread

# রেন্ডার এরর বন্ধ করার জন্য এই অংশটুকু
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- তোমার বটের আসল কোড এখানে ---
# এখানে তোমার বটের টোকেনটা দিবা
API_TOKEN = '7615998188:AAH1W8W3N2vYFmD5-R_XG_VOfu-3S95K58U'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "আলহামদুলিল্লাহ! আপনার বট এখন সচল আছে।")

# বট চালু করার আগে keep_alive ফাংশন কল করতে হবে
keep_alive()

print("Bot is starting...")
bot.infinity_polling()
