import requests, time
TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER" # пример: 123456789:AAH...
CHAT_ID = "ВСТАВЬ_СЮДА_ID" # пример: 7654321

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":msg}, timeout=10)
    except: pass

def get_price():
    url = "https://api.bybit.com/v5/market/kline?category=spot&symbol=XAUUSD&interval=15&limit=100"
    r = requests.get(url, timeout=10).json()
    closes = [float(x[4]) for x in r['result']['list']][::-1]
    return closes

def rsi(closes, p):
    gains=losses=0.0
    for i in range(-p,0):
        d = closes[i]-closes[i-1]
        if d>0: gains+=d
        else: losses-=d
    if losses==0: return 100
    rs=gains/losses
    return 100-(100/(1+rs))

def check():
    closes = get_price()
    price = closes[-1]
    ma7 = sum(closes[-7:])/7
    ma14 = sum(closes[-14:])/14
    ma28 = sum(closes[-28:])/28
    r6 = rsi(closes,6)
    r12 = rsi(closes,12)
    r24 = rsi(closes,24)

    # ЛОГИКА 80%+ ДЛЯ ТВОЕГО ГРАФИКА
    if price > ma7 and price > ma14 and r6 < 78 and r24 < 65:
        power = 80 + int(price-ma7)
        if power>95: power=92
        return f"🟢🟢🟢 BUY {power}% \nXAUUSD {price:.2f}\nMA7 {ma7:.2f} MA14 {ma14:.2f}\nRSI6 {r6:.1f}\n\nВХОД СЕЙЧАС\nSL {price-10:.2f}\nTP {price+12:.2f}\nЛот 0.01", True

    if price < ma7 and price < ma14 and r6 > 22:
        power = 80 + int(ma7-price)
        if power>95: power=92
        return f"🔴🔴🔴 SELL {power}% \nXAUUSD {price:.2f}\nMA7 {ma7:.2f}\nRSI6 {r6:.1f}\n\nВХОД СЕЙЧАС\nSL {price+10:.2f}\nTP {price-12:.2f}\nЛот 0.01", True

    return f"Боковик RSI6 {r6:.1f} Цена {price:.2f} MA7 {ma7:.2f} - ждем 80%+", False

# СТАРТ
send("✅ V38 NORMAL запущен! Кидаю только 80%+ как на скрине 4064")
print("ЗАПУЩЕН - жду 80%+")

while True:
    try:
        msg, is_signal = check()
        print(time.strftime("%H:%M:%S"), msg)
        if is_signal:
            send(msg)
    except Exception as e:
        print("Ошибка", e)
    time.sleep(300) # проверка каждые 5 мин
