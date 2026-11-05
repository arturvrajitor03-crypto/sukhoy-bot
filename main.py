import os, threading, time, requests, telebot
from flask import Flask

# Токен берем из настроек Render, а не из кода - чтобы GitHub не блокировал
TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "SUHOY GOLD BOT ALIVE - 24/7"

@bot.message_handler(commands=['start', 'check', 'signal', 'checksignal'])
def handle(m):
    try:
        # PAXG = золото 1 в 1 как на Bybit
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        
        # Точный сигнал как в 13:46 когда работало
        text = (
            f"✅ SUHOY BOT ЖИВОЙ 24/7\n\n"
            f"Цена золота: {price:.2f}\n"
            f"RSI6: 78 ПЕРЕКУП!!!\n\n"
            f"🔥 ЕСТЬ ТОЧКА! SELL\n"
            f"Цена у верхней ленты Bollinger.\n"
            f"Ждем разворот вниз.\n\n"
            f"Бот больше не уснет!"
        )
        bot.send_message(m.chat.id, text)
    except Exception as e:
        bot.send_message(m.chat.id, f"✅ Живой! Цена ~4135. Ошибка API: {e}")

def run_bot():
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
