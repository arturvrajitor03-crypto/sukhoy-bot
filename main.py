import os, threading, time, logging
from flask import Flask
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip().replace('"','').replace("'","")
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN:
        print("BOT_TOKEN missing!"); 
        while True: time.sleep(3600)
    from telegram.ext import Application, CommandHandler
    async def start(update, context):
        await update.message.reply_text("Бот работает! ✅ Напиши /dry")
    async def dry(update, context):
        await update.message.reply_text("🔥 Режим Сухого включен! Бот живой!")
    while True:
        try:
            print("Starting polling...")
            app_bot = Application.builder().token(BOT_TOKEN).build()
            app_bot.add_handler(CommandHandler("start", start))
            app_bot.add_handler(CommandHandler("dry", dry))
            app_bot.run_polling(drop_pending_updates=True)
        except Exception as e:
            print(f"BOT ERROR: {e}")
            import traceback; traceback.print_exc()
            time.sleep(5)
