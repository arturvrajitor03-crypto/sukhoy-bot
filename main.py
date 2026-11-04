import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler
import asyncio
import threading

TOKEN = os.getenv("BOT_TOKEN","").strip()
WEB_URL = "https://sukhoy-bot.onrender.com"

app = Flask(__name__)

# Создаем приложение ТГ
application = Application.builder().token(TOKEN).build()

async def start(update, context):
    await update.message.reply_text("Бот живой! ✅\nПиши /dry")

async def dry(update, context):
    await update.message.reply_text("Принял /dry ✅\nСухой режим включен!")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("dry", dry))

# Для обработки вебхука
async def process_update(data):
    async with application:
        await application.process_update(Update.de_json(data, application.bot))

@app.route('/')
def home():
    return f"BOT OK Token={bool(TOKEN)}"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    asyncio.run(process_update(data))
    return "ok"

def set_webhook():
    import urllib.request
    try:
        # Удаляем старый и ставим новый
        url = f"{WEB_URL}/webhook"
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=10).read()
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={url}", timeout=10).read()
        print(f"Webhook set to {url}", flush=True)
    except Exception as e:
        print(f"Webhook error {e}", flush=True)

# Ставим вебхук в отдельном потоке после старта
threading.Timer(3, set_webhook).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
