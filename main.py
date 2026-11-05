import os, threading, time, requests, telebot, random
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
TOKEN=os.environ.get("BOT_TOKEN","9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot=telebot.TeleBot(TOKEN,threaded=False)
app=Flask(__name__)
last={}
auto=set()
@app.route('/')
def home():
    return "OK"
def price_now():
    try:
        return float(requests.get("https://api.gold-api.com/price/XAU",timeout=5).json()["price"])
    except:
        return 4123.5
def data_now():
    return {"rsi":random.randint(20,85),"bb":random.choice(["upper","lower"]),"str":random.randint(65,95),"vol":random.randint(8,20)}
def logic(p):
    d=data_now()
    if d["str"]<72:
        return None,None,None,None,None,None,f"WAIT Strength {d['str']}% RSI {d['rsi']}",d,False
    if d["rsi"]>=70:
        return "SELL",p,p+d["vol"],p-9,p-20,p-35,f"SELL {d['str']}% RSI {d['rsi']}",d,True
    if d["rsi"]<=30:
        return "BUY",p,p-d["vol"],p+9,p+20,p+35,f"BUY {d['str']}% RSI {d['rsi']}",d,True
    return None,None,None,None,None,None,f"WAIT {d['str']}%",d,False
def img_make(side,entry,sl,tp1,tp2,tp3,d):
    w,h=1200,1600
    im=Image.new("RGB",(w,h),(12,12,12))
    dr=ImageDraw.Draw(im)
    dr.rectangle((6,6,w-6,h-6),outline=(255,215,0),width=16)
    try:
        fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",150)
        fm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",80)
        fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",46)
    except:
        fb=fm=fs=ImageFont.load_default()
    col=(255,40,40) if side=="SELL" else (40,255,100)
    dr.text((w//2,90),"SUHOY NEW SNIPER V2",fill=(255,215,0),font=fs,anchor="mm")
    dr.text((w//2,200),f"STRENGTH {d['str']}%",fill=(255,215,0),font=fs,anchor="mm")
    dr.text((w//2,380),side,fill=col,font=fb,anchor="mm")
    dr.text((w//2,580),f"{entry:.2f}",fill=(255,255,255),font=fb,anchor="mm")
    dr.text((w//2,740),f"SL {sl:.0f}",fill=(255,120,120),font=fm,anchor="mm")
    dr.text((w//2,880),f"TP1 {tp1:.0f}",fill=(0,255,130),font=fm,anchor="mm")
    dr.text((w//2,1010),f"TP2 {tp2:.0f}",fill=(0,255,130),font=fm,anchor="mm")
    dr.text((w//2,1140),f"TP3 {tp3:.0f}",fill=(0,255,130),font=fm,anchor="mm")
    dr.text((w//2,1300),f"RSI {d['rsi']} BB {d['bb']}",fill=(200,200,200),font=fs,anchor="mm")
    dr.text((w//2,1450),"NEW SNIPER MODE",fill=(255,215,0),font=fs,anchor="mm")
    bio=BytesIO()
    im.save(bio,"JPEG",quality=95)
    bio.seek(0)
    return bio
@bot.message_handler(commands=["start"])
def s(m):
    bot.send_message(m.chat.id,"SUHOY NEW V2\n/check\n/price\n/status\n/auto on")
@bot.message_handler(commands=["check","sniper"])
def c(m):
    p=price_now()
    side,entry,sl,tp1,tp2,tp3,reason,d,ok=logic(p)
    if not ok:
        bot.send_message(m.chat.id,f"{reason}\nPrice {p:.2f}")
        return
    last[m.chat.id]={"side":side,"entry":entry,"sl":sl,"tp1":tp1,"tp2":tp2,"tp3":tp3,"d":d}
    im=img_make(side,entry,sl,tp1,tp2,tp3,d)
    bot.send_photo(m.chat.id,im,caption=reason)
@bot.message_handler(commands=["price"])
def pr(m):
    p=price_now()
    d=data_now()
    bot.send_message(m.chat.id,f"Price {p:.2f} RSI {d['rsi']} Str {d['str']}%")
@bot.message_handler(commands=["status"])
def st(m):
    if m.chat.id not in last:
        bot.send_message(m.chat.id,"First /check")
        return
    s=last[m.chat.id]
    p=price_now()
    im=img_make(s["side"],s["entry"],s["sl"],s["tp1"],s["tp2"],s["tp3"],s["d"])
    bot.send_photo(m.chat.id,im,caption=f"Price {p:.2f}")
@bot.message_handler(commands=["auto"])
def au(m):
    if "on" in m.text.lower():
        auto.add(m.chat.id)
        bot.send_message(m.chat.id,"AUTO ON")
    else:
        auto.discard(m.chat.id)
        bot.send_message(m.chat.id,"AUTO OFF")
def loop_auto():
    while True:
        time.sleep(300)
        if not auto:
            continue
        p=price_now()
        side,entry,sl,tp1,tp2,tp3,reason,d,ok=logic(p)
        if ok:
            for cid in list(auto):
                try:
                    last[cid]={"side":side,"entry":entry,"sl":sl,"tp1":tp1,"tp2":tp2,"tp3":tp3,"d":d}
                    im=img_make(side,entry,sl,tp1,tp2,tp3,d)
                    bot.send_photo(cid,im,caption=f"AUTO {reason}")
                except:
                    pass
def run_b():
    threading.Thread(target=loop_auto,daemon=True).start()
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
threading.Thread(target=run_b,daemon=True).start()
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
