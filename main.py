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

# Человек ОБЯЗАТЕЛЬНО должен ПРОСИТЬ!
DEMAND = ["нужен", "нужна", "нужно", "нужны", "ищу", "ищем", "требуется", "требуются", "кто может", "кто сможет", "кто сделает", "помогите найти", "посоветуйте", "сколько стоит", "сколько будет стоить", "нужна помощь", "требуется помощь"]

WORK = ["маляр", "покрасить", "покраска", "шпаклевка", "шпатлевание", "собрать мебель", "сборка мебели", "повесить тв", "мастер на час", "каблан", "бригада", "подряд", "ремонт дома", "ремонт квартиры", "отделочные", "покраска подъезда"]

# Если есть эти фразы - это 100% конкурент, НЕ брать!
STOP_WORDS = ["предлагаю", "предлагаем", "оказываю", "выполняю", "выполняем", "мои услуги", "наши услуги", "по доступным ценам", "по разумным ценам", "быстро, аккуратно", "качество за разумные", "выполняется надёжно", "обращайтесь", "звоните нам", "опыт работы", "лет опыта", "перевозки", "виза", "b1", "b2", "вакансия", "вакансии", "зарплата", "ставка", "ищу работу", "ищу подработку"]

seen = set()

def is_order(text):
    t = text.lower()
    if any(s in t for s in STOP_WORDS):
        return False
    has_demand = any(k in t for k in DEMAND)
    has_work = any(k in t for k in WORK)
    # НУЖНЫ ОБА СЛОВА: человек просит + твоя работа
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
                    if "каблан" in txt.lower() or "бригада" in txt.lower() or "подряд" in txt.lower():
                        msg = f"🏗️ КАБЛАН / БРИГАДА! ЧЕЛОВЕК ИЩЕТ!\n\n📝 {txt[:400]}\n\n🔗 {link}\n\n📞 Звони: {PHONE}"
                    else:
                        msg = f"🔥 НАШЁЛ РАБОТУ! ЧЕЛОВЕК ПРОСИТ!\n\n📝 {txt[:400]}\n\n🔗 {link}\n\n📞 Звони быстро: {PHONE}\n\n❓ Город спроси сам!"
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
    bot.send_message(m.chat.id, f"✅ Бот v9 РАБОТАЕТ! ТОЛЬКО ПРОСЬБЫ!\n\n🔍 Беру ТОЛЬКО: 'НУЖЕН маляр', 'ИЩУ мастера', 'Сколько стоит покрасить'\n❌ НЕ беру: 'Предлагаю услуги', 'Мастер на час в Хайфе', 'По доступным ценам', 'Виза'\n\n📞 Твой номер: {PHONE}")

threading.Thread(target=hunter, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
