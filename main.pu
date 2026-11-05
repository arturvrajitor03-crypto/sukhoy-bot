import os, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
BOT_TOKEN=os.getenv("BOT_TOKEN")
def get_gold():
 try:
  p=float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT",timeout=10).json()['price'])
  k=requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30",timeout=10).json()
  c=[float(x[4]) for x in k]
  g=l=0
  for i in range(1,15):
   d=c[-i]-c[-i-1]
   g+=d if d>0 else 0
   l+=abs(d) if d<0 else 0
  rsi=100 if l==0 else 100-(100/(1+g/14/(l/14)))
  return p,rsi
 except: return None,None
async def start(u,c): await u.message.reply_text("V5 LIVE! /check")
async def check(u,c):
 p,r=get_gold()
 if not p: await u.message.reply_text("Error try /check");return
 msg=f"{p:.1f} RSI {r:.1f} "
 msg+= "BUY 95%" if r<30 else "SELL" if r>70 else "WAIT"
 await u.message.reply_text(msg)
a=Application.builder().token(BOT_TOKEN).build()
a.add_handler(CommandHandler("start",start))
a.add_handler(CommandHandler("check",check))
a.run_polling()
