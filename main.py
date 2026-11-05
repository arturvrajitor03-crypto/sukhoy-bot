import os,io,time,threading
from flask import Flask,request
import telebot
from PIL import Image,ImageDraw,ImageFont
import requests

TOKEN="9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA"
CHAT_ID=None # сюда твой ID канала если хочешь авто-посты
bot=telebot.TeleBot(TOKEN)
app=Flask(__name__)

def get_klines():
 try:
  u="https://api.binance.com/api/v3/klines"
  p={"symbol":"PAXGUSDT","interval":"15m","limit":60}
  r=requests.get(u,params=p,timeout=10).json()
  closes=[float(x[4]) for x in r]
  return closes
 except:
  return [4120,4122,4125,4128,4130,4128]*10

def calc_rsi(prices,period=14):
 gains=0
 losses=0
 for i in range(1,period+1):
  d=prices[-i]-prices[-i-1]
  if d>0:
   gains+=d
  else:
   losses+=-d
 if losses==0:
  return 80
 rs=gains/losses
 return 100-(100/(1+rs))

def calc_ema(prices,period):
 k=2/(period+1)
 ema=prices[0]
 for p in prices:
  ema=p*k+ema*(1-k)
 return ema

def analyze():
 prices=get_klines()
 price=prices[-1]
 rsi=calc_rsi(prices)
 ema20=calc_ema(prices,20)
 ema50=calc_ema(prices,50)
 print(f"CHECK price={price} rsi={rsi} ema20={ema20} ema50={ema50}")
 signal=None
 reason=""
 if rsi<38 and price>ema50 and prices[-1]>prices[-2]:
  signal="BUY"
  reason=f"RSI перепродан {round(rsi,1)} + отбой от EMA50. Хороший выкуп!"
 elif rsi>68 and price<ema50 and prices[-1]<prices[-2]:
  signal="SELL"
  reason=f"RSI перекуплен {round(rsi,1)} + слом EMA50. Хороший шорт!"
 return signal,price,rsi,reason

def make_image(side,entry,rsi,reason):
 W=1080
 H=1450
 img=Image.new('RGB',(W,H),(14,14,14))
 d=ImageDraw.Draw(img)
 try:
  p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
  fb=ImageFont.truetype(p,52)
  fm=ImageFont.truetype(p,36)
  fs=ImageFont.truetype(p,28)
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
 tp3=entry+30 if side=="BUY" else entry-30
 col=(50,255,130) if side=="BUY" else (255,70,70)
 d.text((60,240),side+" "+str(round(entry,1)),font=fb,fill=col)
 d.text((60,320),"RSI "+str(round(rsi,1)),font=fm,fill=(200,200,200))
 d.text((60,400),"ENTRY "+str(round(entry,1)),font=fm,fill=(255,255,255))
 d.text((60,460),"SL "+str(round(sl,1)),font=fm,fill=(255,70,70))
 d.text((60,540),"TP1 "+str(round(tp1,1)),font=fm,fill=(50,255,130))
 d.text((60,600),"TP2 "+str(round(tp2,1)),font=fm,fill=(50,255,130))
 d.text((60,660),"TP3 "+str(round(tp3,1)),font=fm,fill=(50,255,130))
 # причина
 d.text((60,780),reason[:42],font=fs,fill=(212,175,55))
 d.text((60,820),reason[42:84],font=fs,fill=(212,175,55))
 bio=io.BytesIO()
 img.save(bio,'PNG')
 bio.seek(0)
 return bio

@bot.message_handler(commands=['start'])
def start(m):
 bot.send_message(m.chat.id,"Sniper LIVE! /signal /check")

@bot.message_handler(commands=['signal','buy','sell'])
def sig(m):
 s,p,r,rs=analyze()
 if not s:
  s="BUY"
  p=get_klines()[-1]
  r=50
  rs="Рынок в ожидании. Тестовый сигнал"
 bot.send_photo(m.chat.id,make_image(s,p,r,rs),caption=rs)

@bot.message_handler(commands=['check'])
def chk(m):
 s,p,r,rs=analyze()
 if s:
  bot.send_message(m.chat.id,f"🔥 ЕСТЬ СИГНАЛ! {s} {p} RSI {r}\n{rs}")
  bot.send_photo(m.chat.id,make_image(s,p,r,rs))
 else:
  bot.send_message(m.chat.id,f"Пока нет точки. Цена {round(p,1)} RSI {round(r,1)} EMA тренд спокойный. Ждем выкуп.")

@app.route('/')
def home():
 return "SNIPER LIVE"

@app.route('/webhook',methods=['POST'])
def wh():
 bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
 return "ok",200

def loop_check():
 while True:
  try:
   s,p,r,rs=analyze()
   if s and CHAT_ID:
    bot.send_photo(CHAT_ID,make_image(s,p,r,rs),caption=f"🚨 AUTO {s}\n{rs}")
   time.sleep(180)
  except Exception as e:
   print(e)
   time.sleep(180)

#threading.Thread(target=loop_check,daemon=True).start()

if __name__=='__main__':
 app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
