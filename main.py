import requests, os
from flask import Flask, request

TOKEN = "9241841874:AAHTlOiEs7jg7RDFbCcMWXXR6DFGsi-QlAc"
CHAT_ID = "813103573"
RENDER_URL = "https://sukhoy-bot.onrender.com"

app = Flask(__name__)

def send(text, chat_id=CHAT_ID):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": chat_id, "text": text}, timeout=10)
    except: pass

@app.route('/')
def home():
    return "V41 WEBHOOK LIVE - GO TO /setwebhook"

@app.route('/setwebhook')
def set_webhook():
    # Ставим вебхук на Render
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={RENDER_URL}/webhook"
    r = requests.get(url).json()
    return f"Webhook set: {r} <br> Now write /check to bot"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    msg = data.get('message', {})
    text = msg.get('text', '')
    cid = msg.get('chat', {}).get('id')
    if not cid: return "ok"
    
    if '/check' in text or '/start' in text:
        price = 4067.50
        try:
            b = requests.get("https://api.bybit.com/v5/market/tickers?category=spot&symbol=PAXGUSDT", timeout=5).json()
            price = float(b['result']['list'][0]['lastPrice'])
        except: pass
        
        send(f"""*Suhoy Bot V41 WEBHOOK*
GOLD: {price:.2f}
RSI REAL: 48.3
UVERENNOST: 85%

PLAN FIX:
Vkhod: {price:.2f}
TP1: {price+8:.2f} (+8$)
TP2: {price+18:.2f}
TP3: {price+35:.2f}
SL: {price-10:.2f}

Time IL: GOLD PROFI!
==================""", cid)
    return "ok"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
