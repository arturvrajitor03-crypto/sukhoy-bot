import os, io, random, threading, time
from flask import Flask, request
import telebot
from PIL import Image, ImageDraw, ImageFont
import requests

TOKEN = "СЮДА_ВСТАВЬ_НОВЫЙ_ТОКЕН_ИЗ_BOTFATHER"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Храним чаты кто нажал /start
CHATS = set()

def get_data():
    try:
        # Берем свечи золота за 1 час
        url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=100"
        klines = requests.get(url, timeout=10).json()
        closes = [float(k[4]) for k in klines]
        price = closes[-1]
        
        # Считаем EMA 50 и RSI
        ema50 = sum(closes[-50:]) / 50
        # RSI простой
        gains = [max(0, closes[i]-closes[i-1]) for i in range(1,len(closes))]
        losses = [max(0, closes[i-1]-closes[i]) for i in range(1,len(closes))]
        avg_gain = sum(gains[-14:])/14
        avg_loss = sum(losses[-14:])/14
        rsi = 100 - (100/(1+avg_gain/(avg_loss+0.0001)))
        
        return price, ema50, rsi, closes
    except Exception as e:
        print("ERR data", e)
        return 4128.7, 4128.0, 50, [4128.7]*100

def make_image(side, entry, sl, tp1, tp2, tp3, rsi, conf_text="HIGH"):
    W,H=800,1100
    img=Image.new('RGB',(W,H),(11,11,11))
    draw=ImageDraw.Draw(img)
    draw.rectangle([5,5,W-5,H-5], outline=(212,175,55), width=3)
    try:
        fb=ImageFont.truetype("DejaVuSans-Bold.ttf",52)
        fm=ImageFont.truetype("DejaVuSans-Bold.ttf",34)
        fs=ImageFont.truetype("DejaVuSans.ttf",28)
    except:
        fb=fm=fs=ImageFont.load_default()
    
    color = (50,255,100) if side=="BUY" else (255,60,60)
    draw.text((W//2,80), "🐂 SUHOY GOLD", font=fb, anchor="mm", fill=(212,175,55))
    draw.text((W//2,150), f"{'✅ ' if conf_text=='HIGH' else ''}{side} XAUUSD", font=fb, anchor="mm", fill=color)
    draw.text((W//2,205), f"Confidence: {conf_text} | RSI: {rsi:.0f}", font=fs, anchor="mm", fill=(180,180,180))

    y=260
    def line(lbl,val,col=(255,255,255)):
        nonlocal y
        draw.text((60,y), lbl, font=fm, fill=(150,150,150))
        draw.text((W-60,y), f"{val:.1f}", font=fm, anchor="rm", fill=col)
        y+=65
    
    line("ENTRY:", entry, (255,255,255))
    line("STOP LOSS:", sl, (255,70,70))
    y+=15
    line("TP1:", tp1, (50,255,130))
    line("TP2:", tp2, (50,255,130))
    line("TP3:", tp3, (50,255,130))
    
    # Мини-график из реальных цен
    y+=50
    closes = get_data()[3][-30:]
    mn, mx = min(closes), max(closes)
    pts=[]
    for i,c in enumerate(closes):
        x = 60 + i*(W-120)/29
        yy = y+20 + (mx-c)/(mx-mn+0.001)*120
        pts.append((x,yy))
    draw.line(pts, fill=(212,175,55), width=3)

    draw.text((W//2,H-40), "SUHOY AUTO SIGNALS • NOT FINANCIAL ADVICE", font=fs, anchor="mm", fill=(212,175,55))
    bio=io.BytesIO()
    img.save(bio,'PNG')
    bio.seek(0)
    return bio

def check_signal():
    price, ema50, rsi, closes = get_data()
    
    side=None
    # ЛОГИКА ВХОДА - САМАЯ НАДЕЖНАЯ ДЛЯ ЗОЛОТА
    # BUY: цена выше EMA50 и RSI 30-55 (откат)
    if price > ema50 and 32 < rsi < 58 and closes[-1] > closes[-2]:
        side="BUY"
    # SELL: цена ниже EMA50 и RSI 42-68
    elif price < ema50 and 42 < rsi < 68 and closes[-1] < closes[-2]:
        side="SELL"
    
    if side:
        sl = price - 14 if side=="BUY" else price + 14
        tp1 = price + 9 if side=="BUY" else price - 9
        tp2 = price + 18 if side=="BUY" else price - 18
        tp3 = price + 30 if side=="BUY" else price - 30
        conf = "HIGH ✅" if (rsi<45 or rsi>55) else "MEDIUM"
        
        img = make_image(side, price, sl, tp1, tp2, tp3, rsi, conf)
        cap = f"🚨 AUTO SIGNAL FOUND!\n\n{side} XAUUSD {price:.1f}\
