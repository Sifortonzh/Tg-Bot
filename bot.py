import os
import logging
import collections
import openai
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# Keywords to watch
KEYWORDS = ["join", "YouTube", "Netflix", "shared", "vpn", "account", "login", "上车", "合租", "机场", "油管"]

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
stats = {"visits": 0, "keywords": collections.Counter()}

# AI summarization
def ai_summarize(text):
    try:
        if LLM_PROVIDER == "deepseek":
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You summarize Telegram messages related to group coordination."},
                    {"role": "user", "content": f"Summarize this message:
{text}"}
                ],
                "temperature": 0.5
            }
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=10)
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You summarize Telegram messages related to group coordination."},
                    {"role": "user", "content": f"Summarize this message:
{text}"}
                ],
                max_tokens=100
            )
            return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"[AI error: {e}]"

# Greet new users
def greet_user(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        msg = f"Welcome {member.full_name}! Let us know if you need help."
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

# Monitor keywords and summarize
def keyword_listener(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.effective_user.full_name
    stats["visits"] += 1

    if any(kw.lower() in text.lower() for kw in KEYWORDS):
        for kw in KEYWORDS:
            if kw.lower() in text.lower():
                stats["keywords"][kw] += 1

        summary = ai_summarize(text)
        message = f"*Keyword Match Alert*
User: {user}
Summary: {summary}"
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="Markdown")

# Weekly report
def weekly_report(context: CallbackContext):
    report = f"*Weekly Report*
Total messages: {stats['visits']}
"
    for kw, count in stats["keywords"].items():
        report += f"- {kw}: {count} times
"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=report, parse_mode="Markdown")

# Main function
def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_user))
    dp.add_handler(MessageHandler(Filters.text & Filters.group, keyword_listener))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: weekly_report(dp), trigger="interval", weeks=1)
    scheduler.start()

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
