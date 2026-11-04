import os, asyncio, threading, traceback
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
TOKEN=os.getenv("BOT_TOKEN","").strip()
print(f"TOKEN exists: {bool(TOKEN)} len={len(TOKEN)}",flush=True)
app=Flask(__name__)
@app.route('/')
def home(): return f"OK {bool(TOKEN)}"
async def start(update, context):
    print(f"Got /start",flush=True)
    await update.message.reply_text("Бот работает! ✅ Напиши /dry")
async def dry(update, context):
    await update.message.reply_text("Принял: /dry ✅")
def run_bot():
    try:
        print("Init thread...",flush=True)
        async def main():
            print("Creating app...",flush=True)
            application=Application.builder().token(TOKEN).build()
            application.add_handler(CommandHandler("start",start))
            application.add_handler(CommandHandler("dry",dry))
            print("Starting polling...",flush=True)
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            print("Polling started!",flush=True)
            while True: await asyncio.sleep(3600)
        asyncio.run(main())
    except Exception as e:
        print(f"BOT CRASHED: {e}",flush=True)
        traceback.print_exc()
threading.Thread(target=run_bot,daemon=True).start()
print("Thread launched",flush=True)
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
