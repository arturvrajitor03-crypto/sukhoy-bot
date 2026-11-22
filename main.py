import requests
import telebot
import threading
import os
from flask import Flask

BOT_TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
CHAT_ID = "8131803573"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        r = requests.get(url, timeout=10)
        data = r.json()
        return float(data["price"])
    except Exception as e:
        print(f"Error {symbol}: {e}")
        return 0

@bot.message_handler(commands=['start'])
def handle_start(message):
    text = (
        "🤖 Бот работает!\n\n"
        "Команды:\n"
        "/start - проверить бота\n"
        "/btc - цена BTC\n"
        "/eth - цена ETH\n"
        "/all - все цены"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['btc'])
def handle_btc(message):
    price = get_price("BTC")
    bot.reply_to(message, f"🪙 BTC: {price:.2f} USDT")

@bot.message_handler(commands=['eth'])
def handle_eth(message):
    price = get_price("ETH")
    bot.reply_to(message, f"💎 ETH: {price:.2f} USDT")

@bot.message_handler(commands=['all'])
def handle_all(message):
    btc = get_price("BTC")
    eth = get_price("ETH")
    sol = get_price("SOL")
    text = (
        f"📊 Цены:\n\n"
        f"🪙 BTC: {btc:.2f} USDT\n"
        f"💎 ETH: {eth:.2f} USDT\n"
        f"◎ SOL: {sol:.2f} USDT"
    )
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    bot.reply_to(message, "Напиши /start для меню")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot started...")
    bot.polling(none_stop=True, interval=0, timeout=20)
