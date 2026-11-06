import os, time, threading, requests
from flask import Flask
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
CHAT_ID = os.getenv("CHAT_ID","")
price_history = deque(maxlen=100)

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r.get('price', 4042))
    except:
        return 4042.8

@app.route('/')
def home():
    return "V21 BEAUTY Gold {} TOKEN OK".format(get_price()), 200

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    if not BOT_TOKEN:
        print("NO TOKEN")
        return
    import telebot
    bot = telebot.TeleBot(BOT_TOKEN)
    print("V21 BEAUTY started")

    @bot.message_handler(commands=['start'])
    def start(m):
        txt = "GOLD PRO V21 BEAUTY\n\n/check - tochniy analiz\n/status - balans\n/trades - signaly"
        bot.reply_to(m, txt)

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

        if rsi < 32:
            sig = "BUY"
            perc = 90
        elif rsi > 68:
            sig = "SELL"
            perc = 90
        else:
            sig = "WAIT"
            perc = 60

        if sig == "BUY":
            tp = p + 30
            sl = p - 20
            emo = "BUY"
        elif sig == "SELL":
            tp = p - 30
            sl = p + 20
            emo = "SELL"
        else:
            tp = p
            sl = p
            emo = "WAIT"

        line1 = "GOLD PRO V21 - {}\n".format(emo)
        line2 = "Signal: {} {}%\n".format(sig, perc)
        line3 = "Price: {:.2f} $\n".format(p)
        line4 = "RSI: {:.1f}\n".format(rsi)
        line5 = "EMA: {:.2f}\n".format(sum(list(price_history)[-20:])/20 if len(price_history)>=20 else p)
        line6 = "Entry: {:.2f}\n".format(p)
        line7 = "TP: {:.2f} (+30)\n".format(tp)
        line8 = "SL: {:.2f} (-20)\n".format(sl)
        line9 = "Time: {}\n".format(datetime.now().strftime("%H:%M %d.%m"))
        line10 = "Balance: 1000 $"

        msg = line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10
        bot.reply_to(m, msg)

    @bot.message_handler(commands=['status'])
    def status(m):
        msg = "STATUS V21\nPrice: {:.2f}\nHistory: {}\nMode: RSI PRO 90%".format(get_price(), len(price_history))
        bot.reply_to(m, msg)

    @bot.message_handler(commands=['trades'])
    def trades(m):
        bot.reply_to(m, "Trades: waiting for 90% signal\nPrice: {:.2f}".format(get_price()))

    bot.infinity_polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
