import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

BOT=os.getenv("BOT_TOKEN")
app=Flask(__name__)

@app.route('/')
def home():
 return "OK"
async def start(u,c):
     
 await u.message.reply_text("alive /dry")

async def dry(u,c):
 await u.message.reply_text("SELL 3982 BUY 3958")

def run():
 b=ApplicationBuilder().token(BOT).build()
 b.add_handler(CommandHandler("start",start))
 b.add_handler(CommandHandler("dry",dry))
 b.run_polling()

threading.Thread(target=run,daemon=True).start()
app.run(host='0.0.0.0',port=10000)
