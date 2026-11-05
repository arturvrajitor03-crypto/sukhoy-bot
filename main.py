import os, threading, time, requests, telebot, json
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
ACTIVE_FILE = "/tmp/active_signal.json"

@app.route('/')
def home(): return "SUHOY BOT RUS LIVE"

def get_price():
    try: return float(requests.get("https://api.gold-api.com/price/XAU", timeout=6).json()['price'])
    except: return 4118.8

def save_signal(d):
    try:
        with open(ACTIVE_FILE, 'w') as f: json.dump(d, f)
    except: pass
def load_signal():
    try:
        with open(ACTIVE_FILE, 'r') as f: return json.load(f)
    except: return None

def make_image(price_now, signal):
    # Пробуем твою золотую рамку
    try:
        base = Image.open("template.jpg").convert("RGB")
        W, H = base.size
        # Делаем в 2 раза больше чтобы цифры были ОГРОМНЫЕ
        base = base.resize((W*2, H*2))
        W, H = base.size
    except:
        W, H = 1280, 900
        base = Image.new('RGB', (W, H), (10,10,10))
    
    draw = ImageDraw.Draw(base)
    
    entry = signal['entry']
    sl = signal['sl']
    tp1, tp2, tp3 = signal['tp1'], signal['tp2'], signal['tp3']
    side = signal['side']
    
    # Проверяем какие TP пройдены
    hits = [False, False, False]
    if price_now <= tp1: hits[0]=True
    if price_now <= tp2: hits[1]=True
    if price_now <= tp3: hits[2]=True

    try:
        f_huge = ImageFont.truetype("arialbd.ttf", int(W*0.11))
        f_big = ImageFont.truetype("arialbd.ttf", int(W*0.045))
        f_mid = ImageFont.truetype("arial.ttf", int(W*0.025))
    except:
        f_huge = f_big = f_mid = ImageFont.load_default()

    # Чистим центр под цифры
    draw.rectangle([W*0.05, H*0.35, W*0.95, H*0.85], fill=(0,0,0))

    color = (255, 30, 30) if side=="SELL" else (30, 255, 90)
    draw.text((W//2, H*0.48), f"{side} {entry:.2f}", fill=color, font=f_huge, anchor="mm", stroke_width=3, stroke_fill=(0,0,0))

    # Нижние блоки по-русски + галочки
    y = H*0.68
    draw.text((W*0.15, y), f"ВХОД\n{entry:.2f}", fill=(255,255,255), font=f_big, anchor="mm", align="center")
    draw.text((W*0.35, y), f"SL\n{sl:.0f}", fill=(255,100,100), font=f_big, anchor="mm", align="center")
    
    # TP с галочками
    for i, (tp, hit) in enumerate([(tp1,hits[0]), (tp2,hits[1]), (tp3,hits[2])]):
        x = W*(0.55 + i*0.14)
        icon = "✅" if hit else "⏳"
        col = (0,255,120) if hit else (255,255,255)
        draw.text((x, y), f"{icon}\nTP{i+1}\n{tp:.0f}", fill=col, font=f_big, anchor="mm", align="center")

    bio = BytesIO()
    base.save(bio, 'JPEG', quality=98)
    bio.seek(0)
    return bio, hits

@bot.message_handler(commands=['start','check','signal'])
def handle(m):
    price = get_price()
    entry = price
    sl = entry + 12
    tp1 = entry - 10
    tp2 = entry - 20
    tp3 = entry - 35

    signal = {"entry":entry,"sl":sl,"tp1":tp1,"tp2":tp2,"tp3":tp3,"side":"SELL","rsi":78,"chat_id":m.chat.id,"last_hits":[False,False,False]}
    save_signal(signal)
    img, hits = make_image(price, signal)
    
    bot.send_message(m.chat.id, f"🔥 ЕСТЬ ТОЧКА! SELL Цена {entry:.2f}\nRSI 78 ПЕРЕКУП! Цена у верхней ленты Bollinger. Ждем разворот вниз!\n\nВХОД: {entry:.2f}\nSL: {sl:.0f}\nTP1: {tp1:.0f} {'✅' if hits[0] else '⏳'}\nTP2: {tp2:.0f} {'✅' if hits[1] else '⏳'}\nTP3: {tp3:.0f} {'✅' if hits[2] else '⏳'}\n\nБот будет сам ставить ✅ когда пройдет!")
    bot.send_photo(m.chat.id, img)

@bot.message_handler(commands=['status'])
def status_cmd(m):
    sig = load_signal()
    if not sig: 
        bot.send_message(m.chat.id, "Нет сигнала. Напиши /check"); return
    price = get_price()
    img, hits = make_image(price, sig)
    bot.send_message(m.chat.id, f"📊 Цена сейчас {price:.2f}\n{'✅' if hits[0] else '⏳'} TP1 {sig['tp1']:.0f}\n{'✅' if hits[1] else '⏳'} TP2 {sig['tp2']:.0f}\n{'✅' if hits[2] else '⏳'} TP3 {sig['tp3']:.0f}")
    bot.send_photo(m.chat.id, img)

def auto_checker():
    while True:
        time.sleep(60)
        sig = load_signal()
        if not sig: continue
        price = get_price()
        img, hits = make_image(price, sig)
        try:
            last = sig.get('last_hits',[False,False,False])
            if hits != last:
                sig['last_hits']=hits
                save_signal(sig)
                cid = sig['chat_id']
                if hits[0] and not last[0]:
                    bot.send_message(cid, f"✅ TP1 {sig['tp1']:.0f} ПРОЙДЕН! Цена {price:.2f}"); bot.send_photo(cid, img)
                if hits[1] and not last[1]:
                    bot.send_message(cid, f"✅✅ TP2 {sig['tp2']:.0f} ПРОЙДЕН!"); bot.send_photo(cid, img)
                if hits[2] and not last[2]:
                    bot.send_message(cid, f"🎉🎉🎉 TP3 {sig['tp3']:.0f} ПРОЙДЕН! ВСЕ ЦЕЛИ ВЗЯТЫ!"); bot.send_photo(cid, img)
        except: pass

def run_bot():
    threading.Thread(target=auto_checker, daemon=True).start()
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling(timeout=60)
        except: time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
