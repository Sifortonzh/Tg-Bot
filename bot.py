from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import collections
import os

# === 配置项 ===
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', 'YOUR_TELEGRAM_ID_HERE')

KEYWORDS = ["上车", "YouTube", "Netflix", "合租", "机场", "油管"]

# === 日志设置 ===
logging.basicConfig(filename='logs/bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# === 统计信息 ===
stats = {
    "visits": 0,
    "keywords": collections.Counter(),
}

def greet_user(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        msg = f"Hi {member.full_name} 👋\nI'm your assistant bot. Please hang tight while we check things out!"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

def keyword_listener(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.effective_user.full_name
    stats["visits"] += 1
    triggered = False

    for kw in KEYWORDS:
        if kw.lower() in text.lower():
            stats["keywords"][kw] += 1
            triggered = True

    if triggered:
        summary = f"{user} 提到了关键词：\n"{text}""
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📬 AI 分析摘要：\n{summary}")

def weekly_report(context: CallbackContext):
    report = f"📊 每周统计\n总触发数：{stats['visits']}\n"
    for kw, count in stats["keywords"].items():
        report += f" - {kw}: {count} 次\n"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=report)

def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_user))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, keyword_listener))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: weekly_report(dispatcher), 'interval', weeks=1)
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
