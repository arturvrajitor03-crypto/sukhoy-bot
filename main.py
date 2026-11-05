import os
import io
from flask import Flask, request
import telebot
from PIL import Image

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_price():
    return 4128.7

def make_signal():
    img = Image.new('RGB', (1080, 1350), (20, 20, 20))
    bio = io.BytesIO()
    img.save(bio, format='JPEG')
    bio.seek(0)
    return bio

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    try:
        t = m.text
        if t is None:
            return
        low = t.lower()
        if '/start' in low:
            bot.send_message(m.chat.id, 'Bot LIVE! Pishi /signal')
        if '/signal' in low or 'buy' in low or 'sell' in low:
            price = get_price()
            img = make_signal()
            direction = 'BUY'
            if 'sell' in low:
                direction = 'SELL'
            cap = direction + ' XAUUSD ' + str(price)
            bot.send_photo(m.chat.id, img, caption=cap)
    except:
        pass

@app.route('/')
def home():
    return 'SUHOY LIVE', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.data.decode('utf-8')
        upd = telebot.types.Update.de_json(data)
        bot.process_new_updates((upd,))
    except:
        pass
    return 'ok', 200

if __name__ == '__main__':
    p = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=p)
