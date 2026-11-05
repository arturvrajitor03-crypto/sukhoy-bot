import os
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardRemove

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    TOKEN = '123456:TEST_DUMMY'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, 'Avto vhod vkluchen! Bot LIVE! Pishi /signal', reply_markup=ReplyKeyboardRemove())

@bot.message_handler(commands=['signal','buy','sell'])
def sig(m):
    bot.send_message(m.chat.id, 'SUHOY XAUUSD BUY 4128 SL 4120 TP 4136 - eto test, seychas dobavim kartinku')

@app.route('/')
def home():
    return 'SUHOY LIVE', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.data.decode('utf-8')
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])
    except:
        pass
    return 'ok', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=port)
