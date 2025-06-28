import os
import logging
import collections
import openai

from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

# === Environment Config ===
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', 'YOUR_TELEGRAM_ID_HERE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

KEYWORDS = ["join", "YouTube", "Netflix", "shared", "vpn", "account", "login", "上车", "合租", "机场", "油管"]

# === Logging Setup ===
logging.basicConfig(filename='logs/bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# === Statistics Tracking ===
stats = {
    "visits": 0,
    "keywords": collections.Counter(),
}

# === Greet New Members ===
def greet_user(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        message = f"Hey {member.full_name}! 🎉\nWelcome aboard 👋 Let us know what you need — we got you 🚀"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# === AI Summary via OpenAI ===
def ai_summarize(text):
    model = os.getenv("LLM_PROVIDER", "openai")
    try:
        if model == "deepseek":
            import requests
            DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
            DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that summarizes Telegram messages about account sharing or subscription coordination."},
                    {"role": "user", "content": f"Summarize this message in 1 sentence:\n{text}"}
                ],
                "temperature": 0.5
            }
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=10)
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes Telegram messages about account sharing or subscription coordination."},
                    {"role": "user", "content": f"Summarize this message in 1 sentence:\n{text}"}
                ],
                max_tokens=100
            )
            return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"[AI error: {e}]"
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

# === Weekly Summary Report ===
def weekly_report(context: CallbackContext):
    report = f"📊 *Weekly Report’s Here!* 🗂️\nTotal messages tracked: `{stats['visits']}`\nHere’s what triggered alerts this week:\n"
    for kw, count in stats["keywords"].items():
        report += f"• `{kw}` → *{count}x* 📈\n"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=report)

# === Main Bot Logic ===
def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_user))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, keyword_listener))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: weekly_report(dispatcher), 'interval', weeks=1)
    scheduler.start()

    print("🤖 Bot is now live and vibin' 🚀")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
