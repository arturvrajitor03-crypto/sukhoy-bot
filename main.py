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
    if hasattr(d1h.columns,"nlevels") and d1h.columns.nlevels>1: d1h.columns=d1h.columns.get_level_values(0)
    d1h=d1h.dropna(); s=pd.Series(d15["Close"].values.flatten()); s1h=pd.Series(d1h["Close"].values.flatten())
    price=float(s.iloc[-1]); ema50=float(s.ewm(span=50).mean().iloc[-1]); e200=float(s1h.ewm(span=200).mean().iloc[-1])
    trend="UP" if price>e200 else "DOWN"; delta=s.diff(); gain=delta.where(delta>0,0).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
    rsi=float(100-(100/(1+gain/loss.iloc[-1]))); e12=s.ewm(span=12).mean(); e26=s.ewm(span=26).mean(); macd=e12-e26; ms=macd.ewm(span=9).mean()
    ma20=s.rolling(20).mean(); sd=s.rolling(20).std(); bbu=float(ma20.iloc[-1]+2*sd.iloc[-1]); bbl=float(ma20.iloc[-1]-2*sd.iloc[-1])
    hi=d15["High"].values.flatten(); lo=d15["Low"].values.flatten(); cl=d15["Close"].values.flatten()
    tr=np.maximum(hi[1:]-lo[1:],np.maximum(abs(hi[1:]-cl[:-1]),abs(lo[1:]-cl[:-1]))); atr=float(pd.Series(tr).rolling(14).mean().iloc[-1])
    atr=max(5,min(20,atr)); h5=float(s.max()); l5=float(s.min()); f618=round(h5-(h5-l5)*0.618,2); f382=round(h5-(h5-l5)*0.382,2)
    return dict(price=price,ema50=ema50,trend=trend,rsi=rsi,macd=float(macd.iloc[-1]),ms=float(ms.iloc[-1]),bbu=bbu,bbl=bbl,atr=atr,f618=f618,f382=f382,df=d15)
def calc(d):
    p=d["price"]; buy=0; sell=0
    if d["trend"]=="UP": buy+=3
    else: sell+=3
    if p>d["ema50"]: buy+=1
    else: sell+=1
    if d["macd"]>d["ms"]: buy+=1
    else: sell+=1
    if 50<d["rsi"]<68: buy+=1
