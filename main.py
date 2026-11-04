import os, asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

async def start(update, context):
    await update.message.reply_text("Бот живой! ✅\nЯ работаю! Пиши /dry")

async def dry(update, context):
    await update.message.reply_text("Принял /dry ✅\nСухой режим!")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("dry", dry))

@app.route('/')
def home():
    return f"BOT OK Token={bool(TOKEN)}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)

        async def run():
            if not application._initialized:
                await application.initialize()
            await application.process_update(update)

        asyncio.run(run())
        return "ok"
    except Exception as e:
        print(f"ERROR {e}", flush=True)
        return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
