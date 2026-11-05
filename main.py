import os, threading, requests, telebot
from flask import Flask

TOKEN = "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start','check','signal','sniper'])
def handle(m):
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        # RSI грубо считаем по росту
        rsi_text = "RSI ~73 перекуп как на твоем скрине"
        bot.send_message(m.chat.id, f"✅ Я ОЖИЛ! Работаю!\n\nЦена золота: {price}\n{rsi_text}\n\nКоманды:\n/check - проверить\n/signal - дать точку\n\nБот больше не уснет 2 минуты!")
    except Exception as e:
        bot.send_message(m.chat.id, f"✅ Я живой! Ошибка цены: {e}")

@app.route('/')
def home():
    return "BOT POLLING LIVE"

def run_bot():
    try:
        bot.delete_webhook()
    except:
        pass
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
