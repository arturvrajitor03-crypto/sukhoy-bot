import os
from flask import Flask, request
import telebot

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN не установлен в Render!")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- ТВОИ КОМАНДЫ БОТА ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я Сухой Артур на связи! Бот заработал ✅\nНапиши /help")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, "Я работаю! Напиши что нужно почистить.")

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    bot.send_message(message.chat.id, f"Принял: {message.text}")

# --- ВЕБХУК - САМОЕ ГЛАВНОЕ ---
@app.route('/')
def index():
    return "Bot is running!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        return 'error', 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
