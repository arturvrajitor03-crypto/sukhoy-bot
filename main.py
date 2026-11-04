import os
import threading
import urllib.request
from flask import Flask
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("BOT_TOKEN", "").strip()

app = Flask(__name__)

@app.route('/')
def home():
    return f"BOT OK Token={bool(TOKEN)}"

async def start(update, context):
    await update.message.reply_text("Бот живой! ✅ Пиши /dry")

async def dry(update, context):
    await update.message.reply_text("Принял /dry ✅ Работаем!")

def run_bot():
    print("=== BOT THREAD START ===", flush=True)
    if not TOKEN:
        print("NO TOKEN", flush=True)
        return
    # Авто-удаление вебхука
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=10).read()
        print("=== WEBHOOK DELETED ===", flush=True)
    except Exception as e:
        print(f"Webhook delete fail: {e}", flush=True)

    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("dry", dry))
        print("=== POLLING STARTED ===", flush=True)
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"=== BOT CRASHED: {e} ===", flush=True)

threading.Thread(target=run_bot, daemon=True).start()
print("=== THREAD LAUNCHED ===", flush=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
