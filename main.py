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

KEYWORDS = [
"нужен маляр", "нужен мастер", "ищу маляра", "ищу мастера",
"покрасить", "покраска", "шпаклевка", "собрать мебель",
"сборка мебели", "повесить тв", "мастер на час",
"каблан", "каблан ищет", "нужен каблан", "ищу каблана",
"бригада", "нужна бригада", "ищу бригаду", "есть бригада",
"подряд", "субподряд", "подрядчик", "субподрядчик",
"нужны рабочие", "ищу рабочих",
"объект", "покраска подъезда",
"ремонт дома", "ремонт квартиры", "отделочные работы",
"требуется бригада", "срочно нужны"
]

# СТОП-СЛОВА - НЕ ПРИСЫЛАТЬ!
STOP_WORDS = ["виза", "b1", "b2", "b-1", "b-2", "вакансия", "вакансии",
"требуются рабочие", "требуется рабочий", "работа в компании",
"работа на компанию", "официальное трудоустройство",
"разрешение на работу", "ищем рабочих в компанию",
"приглашаем на работу", "зарплата", "ставка", "оклад",
"график работы", "полный день", "полная занятость"]

seen = set()

def is_order(text):
    t = text.lower()
    # Если есть стоп-слово - пропускаем!
    if any(s in t for s in STOP_WORDS):
        return False
    # Город БОЛЬШЕ НЕ НУЖЕН! Только слово про работу!
    has_work = any(k in t for k in KEYWORDS)
    return has_work and PHONE not in t

def check_site(name, url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True)[:120]:
            txt = a.get_text(" ", strip=True)
            if len(txt) > 20 and is_order(txt):
                link = a["href"]
                if not link.startswith("http"):
                    link = url + link
                if link not in seen:
                    seen.add(link)
                    if "каблан" in txt.lower() or "бригада" in txt.lower() or "подряд" in txt.lower():
                        msg = f"🏗️ КАБЛАН / БРИГАДА! БОЛЬШОЙ ЗАКАЗ!\n\n📝 {txt}\n\n🔗 {link}\n\n📞 У нас есть бригада! Звони: {PHONE}"
                    else:
                        msg = f"🔥 НАШЁЛ ЗАКАЗ!\n\n📝 {txt}\n\n🔗 {link}\n\n📞 Звони быстро: {PHONE}\n\n❓ Город спроси сам!"
                    bot.send_message(MY_ID, msg)
    except Exception as e:
        print(name, "error:", e)

def hunter():
    while True:
        check_site("DoskaTV", "https://doskatv.co.il")
        check_site("IL4RU", "https://il4ru.com")
        time.sleep(600)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, f"✅ Бот v6 РАБОТАЕТ! БЕЗ ГОРОДА!\n\n🔍 Ищу ВСЕ заказы - даже без города!\nТы сам спросишь у клиента где он.\n\n❌ НЕ присылаю: виза, B1, B2, вакансии\n\n📞 Твой номер: {PHONE}")

threading.Thread(target=hunter, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
