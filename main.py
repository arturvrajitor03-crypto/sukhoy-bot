import os,io
from flask import Flask,request
import telebot
from PIL import Image,ImageDraw,ImageFont
import requests

TOKEN="9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA"
bot=telebot.TeleBot(TOKEN)
app=Flask(__name__)

def get_price():
 try:
  u="https://api.binance.com/api/v3/ticker/price"
  r=requests.get(u,params={"symbol":"PAXGUSDT"},timeout=5).json()
  return float(r['price'])
 except:
  return 4128.7

def make_image(side,entry):
 W=1080
 H=1350
 img=Image.new('RGB',(W,H),(14,14,14))
 d=ImageDraw.Draw(img)
 try:
  p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
  fb=ImageFont.truetype(p,52)
  p2="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
  fm=ImageFont.truetype(p2,44)
 except:
  fb=ImageFont.load_default()
  fm=fb
 d.rectangle([10,10,W-10,H-10],outline=(212,175,55),width=6)
 d.rectangle([0,0,W,180],fill=(212,175,55))
 d.text((40,45),"SUHOY GOLD",font=fb,fill=(0,0,0))
 sl=entry-14 if side=="BUY" else entry+14
 tp1=entry+9 if side=="BUY" else entry-9
 tp2=entry+18 if side=="BUY" else entry-18
 tp3=entry+30 if side=="BUY" else entry-30
 col=(50,255,130) if side=="BUY" else (255,70,70)
 t1=side+" "+str(round(entry,1))
 t2="ENTRY "+str(round(entry,1))
 t3="SL "+str(round(sl,1))
 t4="TP1 "+str(round(tp1,1))
 t5="TP2 "+str(round(tp2,1))
 t6="TP3 "+str(round(tp3,1))
 d.text((60,240),t1,font=fb,fill=col)
 d.text((60,360),t2,font=fm,fill=(255,255,255))
 d.text((60,440),t3,font=fm,fill=(255,70,70))
 d.text((60,560),t4,font=fm,fill=(50,255,130))
 d.text((60,640),t5,font=fm,fill=(50,255,130))
 d.text((60,720),t6,font=fm,fill=(50,255,130))
 bio=io.BytesIO()
 img.save(bio,'PNG')
 bio.seek(0)
 return bio

@bot.message_handler(commands=['start'])
def start(m):
 bot.send_message(m.chat.id,"Bot LIVE! /signal")

@bot.message_handler(commands=['signal','buy','sell'])
def sig(m):
 p=get_price()
 s="SELL" if "sell" in m.text.lower() else "BUY"
 bot.send_photo(m.chat.id,make_image(s,p))

@app.route('/')
def home():
 return "LIVE"

@app.route('/webhook',methods=['POST'])
def wh():
 bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
 return "ok",200

if __name__=='__main__':
 app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
