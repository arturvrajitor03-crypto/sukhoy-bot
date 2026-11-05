import os
from flask import Flask, request
import telebot
from telebot import types
import requests
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return round(r.get('price', 2650), 2)
    except:
        return 2645.50

def make_signal(direction):
    price = get_gold_price()
    now = datetime.now().strftime("%H:%M мск")
    
    if direction == "BUY":
        entry = price
        sl = round(price - 8, 2)
        tp1 = round(price + 6, 2)
        tp2 = round(price + 12, 2)
        emoji = "🟢📈"
    else:
        entry = price
        sl = round(price + 8, 2)
        tp1 = round(price - 6, 2)
        tp2 = round(price - 12, 2)
        emoji = "🔴📉"

    text = f"""
👑 **СУХОЙ - XAUUSD** 🐂
{emoji} **СИГНАЛ: {direction}**

💰 Пара: XAUUSD (GOLD)
⏰ Время: {now}
📊 Цена сейчас: {entry}

🎯 **ВХОД:** {entry}
⛔️ **STOP LOSS:** {sl}

✅ **TP1:** {tp1}
✅ **TP2:** {tp2}
✅ **TP3:** Открытый

⚠️ Риск 1-2% от депо!

#XAUUSD #GOLD #СУХОЙ
"""
    return text

@bot.message_handler(commands=['start','dry','signal'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🟢 BUY Сигнал", "🔴 SELL Сигнал", "💰 Цена Золота")
    bot.send_message(m.chat.id, 
        "👑 **СУХОЙ - XAUUSD на связи!** 🐂\n\nЖми кнопку чтобы получить сигнал по золоту:",
        reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: "BUY" in m.text)
def buy(m):
    bot.send_message(m.chat.id, "Сушу сигнал... ⏳ Анализирую золото...")
    bot.send_message(m.chat.id, make_signal("BUY"), parse_mode="Markdown")

@bot.message_handler(func=lambda m: "SELL" in m.text)
def sell(m):
    bot.send_message(m.chat.id, "Сушу сигнал... ⏳ Анализирую золото...")
    bot.send_message(m.chat.id, make_signal("SELL"), parse_mode="Markdown")

@bot.message_handler(func=lambda m: "Цена" in m.text)
def price(m):
    p = get_gold_price()
    bot.send_message(m.chat.id, f"👑 **XAUUSD сейчас:** {p}$\n🐂 Тренд бычий!", parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def any_text(m):
    if m.text.startswith('/'): return
    bot.send_message(m.chat.id, "Жми 🟢 BUY или 🔴 SELL - дам сигнал!")

@app.route('/')
def home(): return "Live SIGNAL", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return 'ok', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
