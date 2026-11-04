import os, threading, time
from flask import Flask
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"
def run_flask():
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing!")
        while True: time.sleep(3600)
    try:
        from telegram.ext import Application, CommandHandler
        async def start(update, context):
            await update.message.reply_text("Бот работает! ✅")
        print(f"Starting bot...")
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.run_polling()
    except Exception as e:
        print(f"BOT ERROR: {e}")
        import traceback
        traceback.print_exc()
        while True: time.sleep(3600)
