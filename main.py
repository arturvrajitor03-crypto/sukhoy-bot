import os, threading, time, requests, telebot, json
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("BOT_TOKEN", "9241841874:AAELImqP5STFIImsLhZLfeyyo6traRdYSPA")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
ACTIVE_FILE = "/tmp/active_signal.json"

@app.route('/')
def home():
    return "SUHOY SNIPER TP TRACKER LIVE"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=6).json()
        return float(r['price'])
    except:
        return 4130.5

def save_signal(data):
    try:
        with open(ACTIVE_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def load_signal():
    try:
        with open(ACTIVE_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def make_image(price_now, signal):
    W, H = 1280, 800
    img = Image.new('RGB', (W, H), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H], outline=(201, 169, 55), width=10)

    try:
        f_huge = ImageFont.truetype("arialbd.ttf", 100)
        f_big = ImageFont.truetype("arialbd.ttf", 55)
        f_mid = ImageFont.truetype("arial.ttf", 28)
    except:
        f_huge = ImageFont.load_default()
        f_big = ImageFont.load_default()
        f_mid = ImageFont.load_default()

    entry = signal['entry']
    sl = signal['sl']
    tp1 = signal['tp1']
    tp2 = signal['tp2']
    tp3 = signal['tp3']
    side = signal['side']
    rsi = signal['rsi']

    hits = [False, False, False]
    if side == "SELL":
        if price_now <= tp1:
            hits[0] = True
        if price_now <= tp2:
            hits[1] = True
        if price_now <= tp3:
            hits[2] = True
    else:
        if price_now >= tp1:
            hits[0] = True
        if price_now >= tp2:
            hits[1] = True
        if price_now >= tp3:
            hits[2] = True

    draw.text((W//2, 40), "GOLD XAU/USD SELL SIGNAL", fill=(201, 169, 55), font=f_mid, anchor="mt")
    color = (255, 30, 30) if side == "SELL" else (30, 255, 90)
    draw.text((W//2, 180), f"{side} {entry:.2f}", fill=color, font=f_huge, anchor="mm")

    y = 350
    draw.text((200, y), f"ENTRY {entry:.2f} RSI {rsi}", fill=(255, 255, 255), font=f_big, anchor="mm")
    draw.text((W-200, y), f"SL {sl:.0f}", fill=(255, 255, 255), font=f_big, anchor="mm")

    y2 = 520
    for i, (tp, hit) in enumerate([(tp1, hits[0]), (tp2, hits[1]), (tp3, hits[2])]):
        yy = y2 + i * 90
        icon = "V" if hit else "o"
        status = "HIT" if hit else "PENDING"
        col = (0, 255, 100) if hit else (201, 169, 55)
        draw.text((200, yy), f"{icon} TP{i+1} {tp:.0f}", fill=col, font=f_big, anchor="lm")
        draw.text((W-300, yy), status, fill=col, font=f_mid, anchor="lm")

    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio, hits

@bot.message_handler(commands=['start', 'check', 'signal'])
def handle(m):
    price = get_price()
    side = "SELL"
    rsi = 78
    entry = price
    sl = entry + 12
    tp1 = entry - 10
    tp2 = entry - 20
    tp3 = entry - 35
    signal = {
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "side": side,
        "rsi": rsi,
        "chat_id": m.chat.id,
        "last_hits": [False, False, False]
    }
    save_signal(signal)
    img, hits = make_image(price, signal)
    bot.send_message(m.chat.id, f"NEW SIGNAL {side} {entry:.2f} TP1 {tp1:.0f} TP2 {tp2:.0f} TP3 {tp3:.0f}")
    bot.send_photo(m.chat.id, img)

@bot.message_handler(commands=['status'])
def status_cmd(m):
    sig = load_signal()
    if not sig:
        bot.send_message(m.chat.id, "No active signal. Send /check")
        return
    price = get_price()
    img, hits = make_image(price, sig)
    txt = f"Price {price:.2f} TP1 {sig['tp1']:.0f} {'HIT' if hits[0] else 'wait'} TP2 {sig['tp2']:.0f} {'HIT' if hits[1] else 'wait'} TP3 {sig['tp3']:.0f} {'HIT' if hits[2] else 'wait'}"
    bot.send_message(m.chat.id, txt)
    bot.send_photo(m.chat.id, img)

def auto_checker():
    while True:
        time.sleep(60)
        sig = load_signal()
        if not sig:
            continue
        price = get_price()
        img, hits = make_image(price, sig)
        try:
            last_hits = sig.get('last_hits', [False, False, False])
            if hits != last_hits:
                sig['last_hits'] = hits
                save_signal(sig)
                chat_id = sig['chat_id']
                if hits[0] and not last_hits[0]:
                    bot.send_message(chat_id, f"TP1 {sig['tp1']:.0f} HIT!")
                    bot.send_photo(chat_id, img)
                if hits[1] and not last_hits[1]:
                    bot.send_message(chat_id, f"TP2 {sig['tp2']:.0f} HIT!")
                    bot.send_photo(chat_id, img)
                if hits[2] and not last_hits[2]:
                    bot.send_message(chat_id, f"TP3 {sig['tp3']:.0f} HIT! ALL DONE!")
                    bot.send_photo(chat_id, img)
        except Exception as e:
            print(e)

def run_bot():
    threading.Thread(target=auto_checker, daemon=True).start()
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
