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

# Человек ДОЛЖЕН искать мастера - только такие слова!
DEMAND = ["нужен", "нужна", "нужно", "нужны", "ищу", "ищем", "требуется", "требуются", "требует", "кто может", "кто сможет", "помогите", "срочно надо"]

# Работа которую ты делаешь
WORK = ["маляр", "маляра", "покрасить", "покраска", "шпаклевка", "шпатлевание", "собрать мебель", "сборка мебели", "повесить тв", "мастер на час", "каблан", "бригада", "подряд", "субподряд", "подрядчик", "ремонт дома", "ремонт квартиры", "отделочные", "покраска подъезда"]

# Конкуренты - НЕ ПРИСЫЛАТЬ!
STOP_WORDS = ["предлагаю", "предлагаем", "оказываю", "оказываем", "выполняю", "выполняем", "мои услуги", "наши услуги", "мои навыки", "перевозки", "работаем", "на связи", "гарантия сохранности", "виза", "b1", "b2", "вакансия", "вакансии", "зарплата", "ставка", "оклад", "работа в компании", "приглашаем на работу"]

seen = set()

def is_order(text):
    t = text.lower()
    if any(s in t for s in STOP_WORDS):
        return False
    # ОБЯЗАТЕЛЬНО: человек ищет + работа твоя
    has_demand = any(k in t for k in DEMAND)
    has_work = any(k in t for k in WORK)
    return has_demand and has_work and PHONE not in t

def check_site(name, url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True)[:150]:
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
                        msg = f"🔥 НАШЁЛ РАБОТУ! ЧЕЛОВЕК ИЩЕТ ТЕБЯ!\n\n📝 {txt}\n\n🔗 {link}\n\n📞 Звони быстро: {PHONE}\n\n❓ Город спроси сам!"
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
    bot.send_message(m.chat.id, f"✅ Бот v7 РАБОТАЕТ! ТОЛЬКО ЗАКАЗЫ!\n\n🔍 Теперь присылаю ТОЛЬКО когда человек пишет:\n'НУЖЕН маляр' / 'ИЩУ мастера'\n\n❌ НЕ присылаю конкурентов:\n'Предлагаю услуги', 'Перевозки', 'Виза', 'Вакансии'\n\n📞 Твой номер: {PHONE}")

threading.Thread(target=hunter, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
