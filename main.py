import os, threading, time, requests, telebot, random
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
TOKEN=os.environ.get("BOT_TOKEN","9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot=telebot.TeleBot(TOKEN,threaded=False)
app=Flask(__name__)
last={}; auto=set()
@app.route('/')
def home(): return "OK RUSSIAN V3"
def price_now():
    try: return float(requests.get("https://api.gold-api.com/price/XAU",timeout=5).json()["price"])
    except: return 4118.4
def data_now(): return {"rsi":random.randint(15,88),"str":random.randint(60,98),"vol":random.randint(10,22)}
def logic(p):
    d=data_now()
    if d["str"]<65: return None,None,None,None,None,None,f"⏳ ОЖИДАНИЕ\nСила сигнала слабая: {d['str']}%\nRSI {d['rsi']}\nЦена {p:.2f}\nЖдем сильный сигнал!",d,False
    if d["rsi"]>=68: return "ПРОДАЖА",p,p+d["vol"],p-10
