import telebot
from telebot import types
import time

API_TOKEN = '8517473053:AAGZamaioWHYrQrrg6cXOrKnIm0_udBGF9s'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7364617700
# 👇 তোর দেওয়া নতুন স্মার্টলিংক এখানে বসিয়ে দিয়েছি
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
                user_data[referrer]['balance'] += 3.0 # রেফার বোনাস ৳৩
                user_data[referrer]['referrals'] += 1
                bot.send_message(referrer, f"👫 অভিনন্দন! নতুন রেফারেলে ৳৩.০ বোনাস পেয়েছেন।")
        
        user_data[chat_id] = {'balance': 1.0 if referrer else 0.0, 'name': message.from_user.first_name, 'referrals': 0, 'last_ad_click': 0}
        if referrer: bot.send_message(chat_id, "🎁 রেফারেল লিঙ্কে জয়েন করায় ৳১.০ বোনাস পেয়েছেন!")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile")
    bot.send_message(chat_id, f"স্বাগতম {message.from_user.first_name}! 🚀\nটাকা আয় করতে Tasks এ ক্লিক করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    text = message.text
    if chat_id not in user_data: return

    if text == "🎯 Tasks":
        send_task(chat_id, 1)
    elif text == "👤 Profile":
        user = user_data[chat_id]
        bot.send_message(chat_id, f"👤 **আপনার প্রোফাইল**\n\n💰 ব্যালেন্স: ৳{round(user['balance'], 2)}\n👫 মোট রেফার: {user['referrals']}")
    elif text == "👑 Leaderboard":
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)[:30]
        lb_text = "🏆 **সেরা ৩০ জন ইউজার**\n\n"
        for i, (uid, uinfo) in enumerate(sorted_users, 1):
            lb_text += f"{i}. {uinfo['name']} - ৳{round(uinfo['balance'], 2)}\n"
        bot.send_message(chat_id, lb_text)
    elif text == "👫 Referral":
        ref_link = f"https://t.me/{(bot.get_me()).username}?start={chat_id}"
        bot.send_message(chat_id, f"👫 **রেফারেল প্রোগ্রাম**\n\nপ্রতি রেফারে পাবেন ৳৩.০\nআপনার বন্ধু পাবে ৳১.০\n\nআপনার লিঙ্ক: {ref_link}")
    elif text == "💰 Wallet":
        if user_data[chat_id]['balance'] < 100:
            bot.send_message(chat_id, f"❌ সর্বনিম্ন উইথড্র ৳১০০। আপনার ব্যালেন্স: ৳{round(user_data[chat_id]['balance'], 2)}")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("বিকাশ (bKash)", callback_data="pay_bkash"),
                       types.InlineKeyboardButton("নগদ (Nagad)", callback_data="pay_nagad"))
            bot.send_message(chat_id, "পেমেন্ট মেথড বেছে নিন:", reply_markup=markup)

def send_task(chat_id, task_no, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("View Ad 🔎", url=AD_LINK, callback_data="clicked_ad"))
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data=f"task_{task_no}"),
               types.InlineKeyboardButton("Skip ⏭️", callback_data=f"skip_{task_no}"))
    msg_text = f"💡 **টাস্ক {task_no}/8**\nবোনাস: ৳০.৯২\n\n১. 'View Ad' এ ক্লিক করুন\n২. ১০ সেকেন্ড অপেক্ষা করুন\n৩. তারপর 'Confirm' চাপুন"
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
        bot.answer_callback_query(call.id, "অ্যাড দেখা শুরু হয়েছে! ১০ সেকেন্ড অপেক্ষা করুন।")
    elif call.data.startswith("task_"):
        elapsed = time.time() - user_data[chat_id].get('last_ad_click', 0)
        if elapsed < 10:
            bot.answer_callback_query(call.id, f"❌ আরও {int(10-elapsed)} সেকেন্ড অ্যাড দেখুন!", show_alert=True)
            return
        num = int(call.data.split("_")[1])
        if num < 8:
            send_task(chat_id, num + 1, call.message.message_id)
        else:
            user_data[chat_id]['balance'] += 0.92
            bot.edit_message_text("🎊 অভিনন্দন! আপনি টাস্ক শেষ করে ৳০.৯২ পেয়েছেন।", chat_id, call.message.message_id)
    elif call.data.startswith("skip_"):
        send_task(chat_id, int(call.data.split("_")[1]), call.message.message_id)
    elif call.data.startswith("pay_"):
        method = call.data.split("_")[1]
        # 👇 এখানে তোর চাওয়া ২৫০, ৫০০, ১০০০ টাকার বাটন দিয়েছি
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("৳১০০", callback_data=f"amt_{method}_100"),
                   types.InlineKeyboardButton("৳২৫০", callback_data=f"amt_{method}_250"),
                   types.InlineKeyboardButton("৳৫০০", callback_data=f"amt_{method}_500"),
                   types.InlineKeyboardButton("৳১০০০", callback_data=f"amt_{method}_1000"))
        bot.edit_message_text(f"কত টাকা তুলতে চান ({method}):", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("amt_"):
        _, method, amount = call.data.split("_")
        msg = bot.send_message(chat_id, f"আপনি ৳{amount} ({method}) বেছে নিয়েছেন।\nআপনার নম্বরটি দিন:")
        bot.register_next_step_handler(msg, process_payment, method, amount)

def process_payment(message, method, amount):
    if message.text in ["🎯 Tasks", "💰 Wallet", "👑 Leaderboard", "👫 Referral", "👤 Profile"]:
        bot.send_message(message.chat.id, "❌ অনুরোধ বাতিল হয়েছে।")
        return
    bot.send_message(ADMIN_ID, f"🔔 **নতুন উইথড্র রিকোয়েস্ট!**\nটাকা: ৳{amount}\nমেথড: {method}\nনম্বর: {message.text}")
    bot.send_message(message.chat.id, f"✅ আপনার ৳{amount} এর অনুরোধ জমা হয়েছে! ১-২ ঘণ্টার মধ্যে পেমেন্ট পাবেন।")

bot.polling()
                
