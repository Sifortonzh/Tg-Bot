import os
import time
import threading
import requests
import logging
import collections
import openai

from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

# === Configuration ===
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', 'YOUR_TELEGRAM_ID_HERE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
RENDER_PING_URL = os.getenv('RENDER_PING_URL', 'https://your-render-url.onrender.com')

openai.api_key = OPENAI_API_KEY

KEYWORDS = ["join", "YouTube", "Netflix", "shared", "vpn", "account", "login", "上车", "合租", "机场", "油管"]

# === Logging ===
logging.basicConfig(filename='logs/bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# === Stats ===
stats = {
    "visits": 0,
    "keywords": collections.Counter(),
}

# === Keep-alive ping ===
def keep_alive():
    def ping():
        while True:
            try:
                requests.get(RENDER_PING_URL)
                print("Keep-alive ping successful.")
            except Exception as e:
                print("Ping failed:", e)
            time.sleep(300)
    t = threading.Thread(target=ping)
    t.daemon = True
    t.start()

# === Greet new users ===
def greet_user(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        message = f"Hi {member.full_name} 👋\nWelcome to the group! Please wait while we check your request."
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# === AI summarization ===
def ai_summarize(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes Telegram messages about account sharing or subscription coordination."},
                {"role": "user", "content": f"Summarize this message in 1 sentence:
{text}"}
            ],
            max_tokens=100
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"[AI error: {e}]"

# === Listen for keywords and summarize ===
def keyword_listener(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.effective_user.full_name
    stats["visits"] += 1
    matched = False

    for kw in KEYWORDS:
        if kw.lower() in text.lower():
            stats["keywords"][kw] += 1
            matched = True

    if matched:
        summary = ai_summarize(text)
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📬 AI Summary:
From: {user}
Content: {summary}")

# === Weekly stats report ===
def weekly_report(context: CallbackContext):
    report = f"📊 Weekly Stats Report
Total messages: {stats['visits']}
Keyword matches:
"
    for kw, count in stats["keywords"].items():
        report += f" - {kw}: {count} times
"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=report)

# === Main runner ===
def main():
    keep_alive()

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_user))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, keyword_listener))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: weekly_report(dispatcher), 'interval', weeks=1)
    scheduler.start()

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
