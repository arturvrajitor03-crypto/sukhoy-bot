import os, asyncio, threading, traceback
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN","").strip()
print(f"TOKEN exists: {bool(TOKEN)}", flush=True)

app = Flask(__name__)
@app.route('/')
def home():
    return f"OK {bool(TOKEN)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Got /start from {update.effective_user.id}", flush=True)
    await update.message.reply_text("Бот работает! ✅ Напиши /dry")

async def dry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Got /dry from {update.effective_user.id}", flush=True)
    await update.message.reply_text("Принял: /dry 🔥 Сухой режим!")

def run_bot():
    try:
        print("Init thread...", flush=True)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("dry", dry))
        print("Starting polling...", flush=True)
        application.run_polling(stop_signals=None, close_loop=False)
        print("Polling OK!", flush=True)
    except Exception as e:
        print(f"BOT CRASHED: {e}", flush=True)
        traceback.print_exc()

threading.Thread(target=run_bot, daemon=True).start()
print("Flask starting...", flush=True)

if __name__ == '__main__':
    port = int(os.getenv("PORT","10000"))
    app.run(host='0.0.0.0', port=port)
