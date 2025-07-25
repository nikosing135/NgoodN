
import json
import requests
from flask import Flask, request

BOT_TOKEN = '8050978808:AAEJCWDQiBw9knVzxnhCsPeTf09bFxNkaVM'
import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)
DATA_FILE = 'users.json'


def load_users():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f)



def get_chatgpt_message():
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "لطفاً یک خبر خوب امروز از ایران یا جهان بده. کوتاه و مثبت."}],
        "max_tokens": 200,
        "temperature": 0.7
    }

    res = requests.post(url, headers=headers, json=data)

    try:
        result = res.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print("OpenAI API Error:", res.status_code, res.text)
        return "⚠️ متأسفانه مشکلی در دریافت خبر خوب از سرور پیش آمد."
        

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=payload)


@app.route(f'/8050978808:AAEJCWDQiBw9knVzxnhCsPeTf09bFxNkaVM', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    chat_id = data['message']['chat']['id']
    users = load_users()
    if chat_id not in users:
        users.append(chat_id)
        save_users(users)
        send_message(chat_id, "✅ شما با موفقیت عضو خبرهای خوب شدید. از فردا صبح، هر روز یه خبر خوب دریافت می‌کنید 🌞")
    else:
        send_message(chat_id, "شما قبلاً عضو شده‌اید. منتظر خبرهای خوب باشید! ✨")
    return 'ok'


@app.route('/send-news', methods=['GET'])
def send_news_to_all():
    message = get_chatgpt_message()
    users = load_users()
    for user_id in users:
        send_message(user_id, f"📢 خبر خوب امروز:\n\n{message}")
    return 'sent'


@app.route('/')
def home():
    return 'Bot is running.'

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
