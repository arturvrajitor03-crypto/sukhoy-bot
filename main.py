import os, asyncio, logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN","").strip()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Создаем бота
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот живой! ✅\nЯ работаю! Пиши /dry")

async def dry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Принял /dry ✅\nСухой режим!")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("dry", dry))

# Инициализируем бота один раз при старте
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(application.initialize())

@app.route('/')
def home():
    return f"BOT OK Token={bool(TOKEN)} Live=True"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        loop.run_until_complete(application.process_update(update))
        return "ok"
    except Exception as e:
        print(f"WEBHOOK ERROR: {e}", flush=True)
        return "error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
