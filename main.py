import os, io
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw
import requests

TOKEN = "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_price():
    try:
        u = "https://api.binance.com/api/v3/ticker/price"
        r = requests.get(u, params={"symbol":"PAXGUSDT"}, timeout=5).json()
        return float(r['price'])
    except:
        return 4128.7

def make_image(side, entry):
    W,H = 800,900
    img = Image.new('RGB',(W,H),(11,11,11))
    d = ImageDraw.Draw(img)
    d.rectangle([5,5,W-5,H-5], outline=(212,175,55), width=3)
    sl = entry-14 if side=="BUY" else entry+14
    tp1 = entry+9 if side=="BUY" else entry-9
    tp2 = entry+18 if side=="BUY" else entry-18
    tp3 = entry+30 if side=="BUY" else entry-30
    d.text((60,80), "SUHOY GOLD "+side, fill=(212,175,55))
    d.text((60,150), "ENTRY "+str(round(entry,1)), fill=(255,255,255))
    d.text((60,210), "SL "+str(round(sl,1)), fill=(255,70,70))
    d.text((60,270), "TP1 "+str(round(tp1,1)), fill=(50,255,130))
    d.text((60,330), "TP2 "+str(round(tp2,1)), fill=(50,255,130))
    d.text((60,390), "TP3 "+str(round(tp3,1)), fill=(50,255,130))
    bio = io.BytesIO()
    img.save(bio,'PNG')
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Bot LIVE! /signal")

@bot.message_handler(commands=['signal','buy','sell'])
def sig(m):
    p = get_price()
    s = "SELL" if "sell" in m.text.lower() else "BUY"
    bot.send_photo(m.chat.id, make_image(s,p))

@app.route('/')
def home():
    return "SUHOY LIVE"

@app.route('/webhook', methods=['POST'])
def wh():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok",200

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
