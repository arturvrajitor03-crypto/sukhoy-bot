import requests, time, threading, os
from bs4 import BeautifulSoup
import telebot
from flask import Flask

TOKEN = "9241841874:AAEzhDrKaYVetMgcyRjq3ywK2YQS0RaRib4"
MY_ID = 8131803573
PHONE = "0549676781"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route("/")
def home():
    return "Bot Rabotaet!"

# Человек ПРОСИТ - только такие!
DEMAND = ["нужен маляр", "нужна маляр", "нужен мастер", "ищу маляра", "ищу мастера", "ищу каблана", "требуется маляр", "требуется бригада", "нужен каблан", "ищу бригаду", "кто может покрасить", "кто покрасит", "нужно покрасить"]

WORK = ["маляр", "покрасить", "покраска", "шпаклевка", "каблан", "бригада", "подряд", "ремонт дома", "ремонт квартиры", "отделочные"]

# КОНКУРЕНТ - если есть хоть одно слово - НЕ БРАТЬ!
STOP_WORDS = ["предлагаю", "предлагаем", "оказываю", "выполняю", "мои услуги", "наши услуги", "по доступным ценам", "по разумным ценам", "быстро, аккуратно", "приеду", "приеду как договорились", "сделал аккуратно", "доводу работу", "замена кранов", "смесителей", "устранение течей", "сантехника", "мелкий ремонт", "сборка мебели", "полки, зеркала", "тв-кронштейны", "обращайтесь", "опыт работы", "лет опыта", "перевозки", "виза", "вакансия", "зарплата", "ищу работу", "ищу подработку", "мастер на час приехал"]

seen = set()

def is_order(text):
    t = text.lower()
    # Сначала проверяем - это конкурент? Если да - сразу НЕТ!
    if any(s in t for s in STOP_WORDS):
        return False
    has_demand = any(k in t for k in DEMAND)
    has_work = any(k in t for k in WORK)
    return has_demand and has_work and PHONE not in t

def check_site(name, url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True)[:200]:
            txt = a.get_text(" ", strip=True)
            parent = a.parent
            if parent:
                txt2 = parent.get_text(" ", strip=True)
                if len(txt2) > len(txt):
                    txt = txt2
            if len(txt) > 20 and len(txt) < 500 and is_order(txt):
                link = a["href"]
                if not link.startswith("http"):
                    link = url + link
                if link not in seen:
                    seen.add(link)
                    msg = f"🔥 НАШЁЛ РАБОТУ! ЧЕЛОВЕК ПРОСИТ!\n\n📝 {txt[:400]}\n\n🔗 {link}\n\n📞 Звони быстро: {PHONE}"
                    bot.send_message(MY_ID, msg)
    except Exception as e:
        print(name, "error:", e)

def hunter():
    while True:
        check_site("DoskaTV", "https://doskatv.co.il")
        check_site("IL4RU", "https://il4ru.com")
        time.sleep(300)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, f"✅ Бот v10 РАБОТАЕТ! ТОЛЬКО ПРОСЬБЫ!\n\n🔍 Беру ТОЛЬКО: 'НУЖЕН маляр', 'ИЩУ мастера', 'НУЖНО ПОКРАСИТЬ'\n❌ НЕ беру: 'Приеду', 'Сделал аккуратно', 'Замена кранов', 'Предлагаю'\n\n📞 Твой номер: {PHONE}")

threading.Thread(target=hunter, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
