import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
price_history = deque(maxlen=100)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get('price', 4042))
    except:
        return 4042.8

@app.route('/')
def home():
    return "V20 OK Gold {} ".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        return
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V20 bot started")

    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, "V20 WORKING\n/check - price\n/status - info")

    @bot.message_handler(commands=['check'])
    def check(m):
        p = get_price()
        price_history.append(p)
        if len(price_history) > 14:
            gains = 0
            losses = 0
            lst = list(price_history)
            for i in range(1, 15):
                d = lst[-i] - lst[-i-1]
                if d > 0:
                    gains += d
                else:
                    losses += -d
            if losses == 0:
                rsi = 80
            else:
                rs = gains / losses
                rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50

        if rsi < 35:
            sig = "BUY"
        elif rsi > 65:
            sig = "SELL"
        else:
            sig = "WAIT"

        msg = "Gold: {:.2f}\nSignal: {}\nRSI: {:.1f}\nTime: {}".format(p, sig, rsi, datetime.now().strftime("%H:%M"))
        bot.reply_to(m, msg)

    @bot.message_handler(commands=['status'])
    def status(m):
        bot.reply_to(m, "V20 OK\nPrice: {}\nHistory: {}".format(get_price(), len(price_history)))

    bot.infinity_polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
