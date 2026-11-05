import os,io,time
from flask import Flask,request
import telebot
from PIL import Image,ImageDraw,ImageFont
import requests

TOKEN="9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA"
bot=telebot.TeleBot(TOKEN)
app=Flask(__name__)

def get_klines():
 try:
  r=requests.get("https://api.gold-api.com/price/XAU",timeout=5).json()
  p=float(r['price'])
  return [p-5,p-2,p,p+1,p]*12
 except:
  return [4120,4122,4125,4128,4130,4128]*10

def calc_rsi(prices):
 gains=0
 losses=0
 for i in range(1,15):
  d=prices[-i]-prices[-i-1]
  if d>0:
   gains+=d
  else:
   losses+=-d
 if losses==0:
  return 75
 rs=gains/losses
 return 100-(100/(1+rs))

def analyze():
 prices=get_klines()
 price=prices[-1]
 rsi=calc_rsi(prices)
 sig=None
 rsn=""
 if rsi<38 and prices[-1]>prices[-2]:
  sig="BUY"
  rsn=f"RSI {round(rsi,1)} перепродан. Выкуп!"
 elif rsi>68 and prices[-1]<prices[-2]:
  sig="SELL"
  rsn=f"RSI {round(rsi,1)} перекуп. Шорт!"
 return sig,price,rsi,rsn

def make_image(side,entry,rsi,reason):
 W=1080
 H=1350
 img=Image.new('RGB',(W,H),(14,14,14))
 d=ImageDraw.Draw(img)
 try:
  fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",52)
  fm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",38)
  fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",26)
 except:
  fb=ImageFont.load_default()
  fm=fb
  fs=fb
 d.rectangle([10,10,W-10,H-10],outline=(212,175,55),width=6)
 d.rectangle([0,0,W,180],fill=(212,175,55))
 d.text((40,45),"SUHOY GOLD SNIPER",font=fb,fill=(0,0,0))
 sl=entry-14 if side=="BUY" else entry+14
 tp1=entry+9 if side=="BUY" else entry-9
 tp2=entry+18 if side=="BUY" else entry-18
 col=(50,255,130) if side=="BUY" else (255,70,70)
 d.text((60,240),side+" "+str(round(entry,1)),font=fb,fill=col)
 d.text((60,320),"RSI "+str(round(rsi,1)),font=fm,fill=(200,200,200))
 d.text((60,400),"ENTRY "+str(round(entry,1)),font=fm,fill=(255,255,255))
 d.text((60,460),"SL "+str(round(sl,1)),font=fm,fill=(255,70,70))
 d.text((60,540),"TP1 "+str(round(tp1,1)),font=fm,fill=(50,255,130))
 d.text((60,600),"TP2 "+str(round(tp2,1)),font=fm,fill=(50,255,130))
 d.text((60,750),reason,font=fs,fill=(212,175,55))
 bio=io.BytesIO()
 img.save(bio,'PNG')
 bio.seek(0)
 return bio

@bot.message_handler(commands=['start'])
def start(m):
 bot.send_message(m.chat.id,"Sniper LIVE! /check /signal")

@bot.message_handler(commands=['signal','buy','sell'])
def sig(m):
 s,p,r,rs=analyze()
 if not s:
  s="BUY"
  rs="Тест. Ждем хорошую точку"
 bot.send_photo(m.chat.id,make_image(s,p,r,rs),caption=rs)

@bot.message_handler(commands=['check'])
def chk(m):
 s,p,r,rs=analyze()
 if s:
  bot.send_message(m.chat.id,f"🔥 ЕСТЬ ТОЧКА! {s} {p} RSI {r}")
  bot.send_photo(m.chat.id,make_image(s,p,r,rs))
 else:
  bot.send_message(m.chat.id,f"Пока нет точки. Цена {round(p,1)} RSI {round(r,1)}. Ждем выкуп!")

@app.route('/')
def home():
 return "SNIPER LIVE"

@app.route('/webhook',methods=['POST'])
def wh():
 bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
 return "ok",200

if __name__=='__main__':
 app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
