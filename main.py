import os, requests, time

TOKEN = os.getenv("BOT_TOKEN")
AUTO = False

def get_signal():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        k = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=30", timeout=10).json()
        closes = [float(x[4]) for x in k]
        g=l=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: g+=d
            else: l+=abs(d)
        rsi = 100 if l==0 else 100-(100/(1+(g/14)/(l/14 or 1)))
        ema = sum(closes[-20:])/20
        sig="WAIT"
        if rsi<32 and price>ema: sig="BUY"
        elif rsi>68 and price<ema: sig="SELL"
        sl = price*0.998 if sig=="BUY" else price*1.002
        tp = price*1.005 if sig=="BUY" else price*0.995
        return price,rsi,sig,sl,tp
    except:
        return None,None,"ERROR",0,0

def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": chat_id, "text": text})

print("V8 ULTRA STARTED")
offset=0
while True:
    try:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=20", timeout=25).json()
        for u in updates.get("result", []):
            offset = u["update_id"]+1
            chat_id = u["message"]["chat"]["id"]
            txt = u["message"].get("text","")
            if txt=="/start":
                send(chat_id, "🤖 V8 ULTRA LIVE!\n/check - сигнал GOLD\n/auto_on - авто\n/auto_off - выкл")
            elif txt=="/check":
                p,rsi,sig,sl,tp = get_signal()
                if not p: send(chat_id, "Ошибка Binance")
                else: send(chat_id, f"GOLD {p:.2f}\nRSI {rsi:.1f}\nSIGNAL {sig}\nSL {sl:.2f} TP {tp:.2f}\nAUTO {'ON' if AUTO else 'OFF'}")
            elif txt=="/auto_on":
                AUTO=True
                send(chat_id, "✅ АВТО ВКЛ! Теперь пиши /check")
            elif txt=="/auto_off":
                AUTO=False
                send(chat_id, "🛑 АВТО ВЫКЛ")
    except Exception as e:
        print(e)
        time.sleep(5)
