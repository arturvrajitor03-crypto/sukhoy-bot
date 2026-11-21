import os, traceback
from io import BytesIO
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import pandas as pd, numpy as np
TOKEN=os.environ.get("BOT_TOKEN") or "123456:ABC"
APP_URL=os.environ.get("RENDER_EXTERNAL_URL","").rstrip("/")
bot=telebot.TeleBot(TOKEN); app=Flask(__name__)
def font(s,b=True):
    try: return ImageFont.truetype("DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf",s)
    except: return ImageFont.load_default()
def pic(direct,price,sl,tp1,tp2,tp3,sila):
    try: img=Image.open("template.jpg").convert("RGB")
    except: return None
    W,H=img.size; draw=ImageDraw.Draw(img)
    col=(0,170,80) if direct=="BUY" else (220,30,30) if direct=="SELL" else (180,150,40)
    arr="▲  BUY" if direct=="BUY" else "▼  SELL" if direct=="SELL" else "⏳  WAIT"
    x0,x1=int(W*0.08),int(W*0.92); y0,y1=int(H*0.60),int(H*0.96)
    draw.rounded_rectangle([x0,y0,x1,y1],radius=30,fill=(255,255,255))
    draw.rounded_rectangle([x0+8,y0+8,x1-8,y1-8],radius=25,outline=(212,175,55),width=3)
    cx=W//2; y=y0+int(H*0.125); st=int(H*0.041)
    draw.text((cx,y0+int(H*0.03)),arr,font=font(int(W*0.09)),fill=col,anchor="mm")
    draw.text((cx,y0+int(H*0.075)),f"Сила: {sila}%",font=font(int(W*0.05)),fill=(180,140,20),anchor="mm")
    draw.text((cx,y),f"Вход: {price:.2f}",font=font(int(W*0.055)),fill=(0,0,0),anchor="mm")
    draw.text((cx,y+st),f"SL: {sl:.2f}",font=font(int(W*0.055)),fill=(180,30,30),anchor="mm")
    draw.text((cx,y+st*2),f"TP1: {tp1:.2f}",font=font(int(W*0.055)),fill=(0,0,0),anchor="mm")
    draw.text((cx,y+st*3),f"TP2: {tp2:.2f}",font=font(int(W*0.055)),fill=(0,0,0),anchor="mm")
    draw.text((cx,y+st*4),f"TP3: {tp3:.2f}",font=font(int(W*0.055)),fill=(0,0,0),anchor="mm")
    buf=BytesIO(); img.save(buf,format="JPEG",quality=92); buf.seek(0); return buf
def get_data():
    import yfinance as yf
    d15=yf.download("GC=F",period="5d",interval="15m",progress=False,auto_adjust=False)
    if hasattr(d15.columns,"nlevels") and d15.columns.nlevels>1: d15.columns=d15.columns.get_level_values(0)
    d15=d15.dropna(); d1h=yf.download("GC=F",period="1mo",interval="1h",progress=False,auto_adjust=False)
    if hasattr(d1h.columns,"nlevels") and d1h.columns.nlevels>1: d1h.columns=d1h.columns.get_level_values
