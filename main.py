import os, threading
from flask import Flask
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("BOT_TOKEN","").strip()
print(f"TOKEN exists: {bool(TOKEN)} len={len(TOKEN)}", flush=True)

app = Flask(__name__)
@app.route('/')
def home():
    return f"OK {bool(TOKEN)} len={len(TOKEN)}"

async def start(update, context):
    print(f"Got /start", flush=True)
    await update.message.reply_text("Бот работает! ✅ Напиши /dry")

async def dry(update, context):
    print(f"Got /dry", flush=True)
    await update.message.reply_text("Принял: /dry ✅ Готов работать!")

def run_bot():
    try:
        print("Starting bot polling...", flush=True)
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("dry", dry))
        print("Polling started!", flush=True)
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"BOT CRASHED: {e}", flush=True)
        import traceback
        traceback.print_exc()

threading.Thread(target=run_bot, daemon=True).start()
print("Thread launched", flush=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
