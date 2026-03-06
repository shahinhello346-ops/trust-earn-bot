import telebot
from telebot import types
from flask import Flask
from threading import Thread

# --- রেন্ডার এরর বন্ধ করার জাদুর কোড ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
# ------------------------------------

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)
AD_LINK = 'https://duepose.com/d31kudur45?key=ce85cd5333821f8ea0668e189f88f30c'

user_data = {}
user_list = []

def get_user(chat_id, name="User"):
    if chat_id not in user_data:
        if chat_id not in user_list: user_list.append(chat_id)
        user_data[chat_id] = {'balance': 0.0, 'referrals': 0, 'name': name, 'ref_by': None, 'tasks_done': 0}
    return user_data[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"স্বাগতম {user['name']}! 🚀\nপ্রতিটি টাস্কের জন্য পাবেন ৳০.৯২। কাজ শুরু করতে নিচের বাটনে ক্লিক করুন।", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    if call.data.startswith("confirm_"):
        task_no = int(call.data.split("_")[1])
        user['tasks_done'] = task_no
        if task_no < 8:
            send_task(chat_id, task_no + 1, call.message.message_id)
        else:
            user['balance'] += 0.92
            bot.edit_message_text("🎊 অভিনন্দন! ৮টি কাজ সফলভাবে শেষ করেছেন। আপনার অ্যাকাউন্টে ৳০.৯২ যোগ করা হয়েছে।", chat_id, call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.first_name)
    
    if message.text == "🎯 Tasks": send_task(chat_id, 1)
    elif message.text == "💰 Wallet":
        bot.send_message(chat_id, f"💰 আপনার ব্যালেন্স: ৳{round(user['balance'], 2)}\nটাকা তুলতে কমপক্ষে ১০০ টাকা লাগবে।")
    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 প্রোফাইল\n💰 ব্যালেন্স: ৳{round(user['balance'], 2)}\n👫 রেফার করেছেন: {user['referrals']}")
    elif message.text == "👫 Referral":
        link = f"https://t.me/TrustEarnCash_bot?start={chat_id}"
        bot.send_message(chat_id, f"👫 প্রতি রেফারে পাবেন ৳৩.০০!\nলিংক: {link}")
    elif message.text == "👑 Leaderboard":
        bot.send_message(chat_id, "👑 লিডারবোর্ড বর্তমানে আপডেট হচ্ছে। খুব শীঘ্রই এটি চালু হবে।")

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"confirm_{task_no}"))
    text = f"💡 টাস্ক নম্বর: {task_no}/৮\n💰 এই টাস্কটি শেষ করলে পাবেন: ৳০.৯২\nবিজ্ঞাপনটি ১৫ সেকেন্ড দেখুন এবং তারপর Confirm বাটনে ক্লিক করুন।"
    if message_id: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else: bot.send_message(chat_id, text, reply_markup=markup)

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.infinity_polling(none_stop=True)
