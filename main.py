import os, requests, threading, time, random
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("BOT_TOKEN","").strip()
app = Flask(__name__)

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        p = float(r.get("price", 0))
        if p > 1000: return int(p)
    except: pass
    return 4093

def get_font(size):
    try: return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except: return ImageFont.load_default()

def create_image(direction, entry, sl, tp1, tp2, tp3):
    img = Image.new("RGB", (1000, 1400), (10,10,10))
    draw = ImageDraw.Draw(img)
    # золотая рамка
    draw.rectangle([5,5,995,1395], outline=(212,175,55), width=8)
    draw.rectangle([30,30,970,1370], outline=(212,175,55), width=2)
    
    font_big = get_font(70)
    font_mid = get_font(42)
    
    # заголовок
    draw.text((300, 50), "СУХОЙ - XAUUSD", fill=(212,175,55), font=font_big)
    
    # направление
    color = (0,255,90) if direction=="BUY" else (255,30,30)
    draw.rectangle([0, 180, 1000, 280], fill=(0,0,0))
    draw.text((330, 200), f"XAUUSD - {direction}", fill=color, font=font_big)
    
    # бык по центру - рисуем круг
    draw.ellipse([350, 350, 650, 650], fill=(212,175,55), outline=(255,215,0), width=5)
    draw.text((440, 460), "🐂", fill=(0,0,0), font=ImageFont.truetype("DejaVuSans-Bold.ttf", 120) if os.path.exists("DejaVuSans-Bold.ttf") else get_font(120))
    
    # блок с данными
    draw.rectangle([100, 800, 900, 1150], fill=(0,0,0))
    draw.rectangle([100, 800, 900, 1150], outline=(212,175,55), width=2)
    
    lines = [f"Вход: {entry}", f"SL: {sl}", f"TP1: {tp1}  ⬜", f"TP2: {tp2}  ⬜", f"TP3: {tp3}  ⬜"]
    y = 830
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_mid)
        w = bbox[2]-bbox[0]
        draw.text(((1000-w)//2, y), line, fill=(255,235,180), font=font_mid)
        y += 65
    
    path = f"/tmp/{random.randint(1,999999)}.jpg"
    img.save(path, quality=95)
    return path

def send_photo(chat_id, photo_path, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as f:
        requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"photo": f}, timeout=20)

def send_text(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)

def set_webhook():
    time.sleep(3)
    base = os.getenv("RENDER_EXTERNAL_URL")
    if base:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={base}/webhook", timeout=10)

threading.Thread(target=set_webhook, daemon=True).start()

@app.route('/')
def home(): return "SUHOY WITH IMAGE LIVE"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()
        if text == "/start":
            send_text(chat_id, "👑 СУХОЙ с картинками!\n/dry - сигнал")
        elif text.startswith("/dry"):
            price = get_gold_price()
            if price >= 4050:
                direction, sl = "BUY", price-9
                tp1, tp2, tp3 = price+4, price+8, price+13
                entry = f"выше {price}"
            else:
                direction, sl = "SELL", price+9
                tp1, tp2, tp3 = price-4, price-8, price-13
                entry = f"ниже {price}"
            
            img_path = create_image(direction, entry, sl, tp1, tp2, tp3)
            caption = f"👑 {direction} {price}$\nTP1 {tp1} ⬜\nTP2 {tp2} ⬜\nTP3 {tp3} ⬜\nСлежу и ставлю ✅"
            send_photo(chat_id, img_path, caption)
    except Exception as e:
        print(e)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
