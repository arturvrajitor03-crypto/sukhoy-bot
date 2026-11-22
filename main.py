import requests
import time
import telebot

BOT_TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
CHAT_ID = "8131803573"

bot = telebot.TeleBot(BOT_TOKEN)

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
    b
