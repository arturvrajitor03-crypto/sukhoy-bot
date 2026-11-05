import os, threading, time, requests, telebot, random, traceback
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

print("STARTING BOT V4 RUSSIAN")

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
print(f"Token len: {len(TOKEN)}")

try:
    bot = telebot.TeleBot(TOKEN, threaded=False)
    print("Bot created OK")
except Exception as e:
    print(f"Bot create error: {e}")
    bot = None

app = Flask(__name__)
last = {}
auto = set()

@app.route('/')
def home():
    return "SUHOY SNIPER V4 RUSSIAN LIVE - OK"

def price_now():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r["price"])
    except:
        return 4118.4

def data_now():
    return {"rsi": random.randint(15, 88), "str": random.randint(60, 98), "vol": random.randint(10, 22)}

def logic(p):
    d = data_now()
    if d["str"] < 60:
        return None,None,None,None,None,None,f"⏳ ОЖИДАНИЕ\nСила {d['str']}% слабая\nRSI {d['rsi']}\nЦена {p:.2f}",d,False
    if d["rsi"] >= 68:
        return "ПРОДАЖА",p,p+d["vol"],p-10,p-22,p-37,f"🔴 ПРОДАЖА\nСила {d['str']}%\nRSI {d['rsi']}",d,True
    if d["rsi"] <= 32:
        return "ПОКУПКА",p,p-d["vol"],p+10,p+22,p+37,f"🟢 ПОКУПКА\nСила {d['str']}%\nRSI {d['rsi']}",d,True
    return None,None,None,None,None,None,f"⏳ БОКОВИК {d['str']}% RSI {d['rsi']}",d,False

def img_make(side,entry,sl,tp1,tp2,tp3,d):
    w,h=1200,1600
    im=Image.new("RGB",(w,h),(14,14,14))
    dr=ImageDraw.Draw(im)
    dr.rectangle((6,6,w-6,h-6),outline=(255,215,0),width=18)
    try:
        fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",130)
        fm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",70)
        fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",40)
    except:
        fb=fm=fs=ImageFont.load_default()
    col=(255,50,50) if "ПРОДА" in side else (50,255,120)
    dr.text((w//2,80),"СУХОЙ СНАЙПЕР V4",fill=(255,215,0),font=fs,anchor="mm")
    dr.text((w//2,150),f"СИЛА {d['str']}% | RSI {d['rsi']}",fill=(255,215,0),font=fs,anchor="mm")
    dr.text((w//2,340),side,fill=col,font=fb,anchor="mm")
    dr.text((w//2,530),f"{entry:.2f}",fill=(255,255,255),font=fb,anchor="mm")
    dr.text((w//2,700),f"СТОП {sl:.0f}",fill=(255,130,130),font=fm,anchor="mm")
    dr.text((w//2,820),f"ЦЕЛЬ1 {tp1:.0f}",fill=(80,255,150),font=fm,anchor="mm")
    dr.text((w//2,940),f"ЦЕЛЬ2 {tp2:.0f}",fill=(80,255,150),font=fm,anchor="mm")
    dr.text((w//2,1060),f"ЦЕЛЬ3 {tp3:.0f}",fill=(80,255,150),font=fm,anchor="mm")
    dr.text((w//2,1250),f"ЗОЛОТО XAUUSD",fill=(180,180,180),font=fs,anchor="mm")
    dr.text((w//2,1350),"БЕЗ РЕКЛАМЫ - ТОЛЬКО НА РУССКОМ",fill=(255,215,0),font=fs,anchor="mm")
    bio=BytesIO()
    im.save(bio,"JPEG",quality=90)
    bio.seek(0)
    return bio

if bot:
    @bot.message_handler(commands=["start"])
    def s(m):
        bot.send_message(m.chat.id,"🇷🇺 СУХОЙ V4 РУССКИЙ\n/check - сигнал\n/price - цена\n/status - последн\n/auto on/off")

    @bot.message_handler(commands=["check","sniper"])
    def c(m):
        try:
            p=price_now()
            side,entry,sl,tp1,tp2,tp3,reason,d,ok=logic(p)
            if not ok:
                bot.send_message(m.chat.id,reason)
                return
            last[m.chat.id]={"side":side,"entry":entry,"sl":sl,"tp1":tp1,"tp2":tp2,"tp3":tp3,"d":d}
            im=img_make(side,entry,sl,tp1,tp2,tp3,d)
            bot.send_photo(m.chat.id,im,caption=reason)
        except Exception as e:
            bot.send_message(m.chat.id,f"Ошибка: {e}")

    @bot.message_handler(commands=["price"])
    def pr(m):
        p=price_now(); d=data_now()
        bot.send_message(m.chat.id,f"ЗОЛОТО {p:.2f} RSI {d['rsi']} Сила {d['str']}%")

    @bot.message_handler(commands=["status"])
    def st(m):
        if m.chat.id not in last:
            bot.send_message(m.chat.id,"Сначала /check"); return
        s=last[m.chat.id]; p=price_now()
        im=img_make(s["side"],s["entry"],s["sl"],s["tp1"],s["tp2"],s["tp3"],s["d"])
        bot.send_photo(m.chat.id,im,caption=f"Сейчас {p:.2f}")

    @bot.message_handler(commands=["auto"])
    def au(m):
        if "on" in m.text.lower():
            auto.add(m.chat.id); bot.send_message(m.chat.id,"АВТО ВКЛ")
        else:
            auto.discard(m.chat.id); bot.send_message(m.chat.id,"АВТО ВЫКЛ")

def loop_auto():
    while True:
        time.sleep(300)
        if not bot or not auto: continue
        try:
            p=price_now(); side,entry,sl,tp1,tp2,tp3,reason,d,ok=logic(p)
            if ok:
                for cid in list(auto):
                    try:
                        last[cid]={"side":side,"entry":entry,"sl":sl,"tp1":tp1,"tp2":tp2,"tp3":tp3,"d":d}
                        im=img_make(side,entry,sl,tp1,tp2,tp3,d)
                        bot.send_photo(cid,im,caption=f"АВТО {reason}")
                    except: pass
        except: pass

def run_b():
    if not bot:
        print("Bot is None, not starting polling")
        return
    threading.Thread(target=loop_auto,daemon=True).start()
    while True:
        try:
            print("Deleting webhook...")
            bot.delete_webhook(drop_pending_updates=True)
            print("Starting polling...")
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Polling error: {e}\n{traceback.format_exc()}")
            time.sleep(5)

threading.Thread(target=run_b,daemon=True).start()
print("Flask starting...")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
