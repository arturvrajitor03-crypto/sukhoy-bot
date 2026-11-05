# Добавь в самое начало после TOKEN:
LAST_CHAT = None

# В цикле while замени send на это:
def send(cid,t):
    global LAST_CHAT
    LAST_CHAT=cid
    try: 
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":cid,"text":t}, timeout=15)
    except Exception as e:
        print(f"Send err: {e}")

# И внизу цикл сделай надежнее:
off=0
while True:
    try:
        r=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={off}&timeout=10", timeout=15).json()
        for x in r.get("result",[]):
            off=x["update_id"]+1
            if "message" not in x: continue
            cid=x["message"]["chat"]["id"]
            CHATS.add(cid)
            text=x["message"].get("text","").strip().lower()
            print(f"Got: {text} from {cid}") # лог
            # ... твои команды ...
            if text=="/trades":
                if not TRADES: send(cid,"📈 Сделок пока нет, ждем сигнал BUY/SELL\n💰 Баланс: 1000$ Боковик 93%")
                else: send(cid,f"📈 Сделок: {len(TRADES)}")
    except Exception as e:
        print(f"Loop err: {e}")
        time.sleep(5)
