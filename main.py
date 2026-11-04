import os, threading
from flask import Flask
import telebot
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is LIVE!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask, daemon=True).start()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAHTlT_eSOdgNcTq2Z_FcDS6P0xoCPdsrmo")
bot = telebot.TeleBot(BOT_TOKEN)
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Бот работает! ✅")
@bot.message_handler(func=lambda m: True)
def echo(m):
    bot.send_message(m.chat.id, f"Принял: {m.text}")
print("Bot started...")
bot.infinity_polling()
