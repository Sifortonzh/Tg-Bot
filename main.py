import os
import json
import logging
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# ========== 环境变量 ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ========== 日志配置 ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== 访客记录 ==========
VISITOR_FILE = "known_visitors.json"

def load_known_visitors():
    if os.path.exists(VISITOR_FILE):
        with open(VISITOR_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_known_visitors(visitor_ids):
    with open(VISITOR_FILE, 'w') as f:
        json.dump(list(visitor_ids), f)

# ========== Deepseek 摘要 ==========
def summarize_with_deepseek(text):
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个 AI 助理，请用简洁自然的语言总结以下用户消息的核心内容。请自动判断用户语言并用合适的语言输出总结。如果你无法判断内容则输出"Ignore"。"},
                {"role": "user", "content": text}
            ],
            "temperature": 0.5
        }
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Deepseek summary failed: {e}")
        return "Summary unavailable."

# ========== 私聊处理 ==========
WELCOME_MESSAGES = {
    "zh": "你好！👋\n我是私聊小助手，你可以在这里留言，我会把内容妥善送达给我家主人 📨",
    "en": "Hey there! 👋\nI'm not the boss — just the intern.\nDrop your message here and I’ll make sure it reaches the top desk. ☕",
    "default": "Hi! 👋 I'm a message assistant. Leave your note, and I’ll forward it."
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id

    if user_id == OWNER_ID:
        return

    known_visitors = load_known_visitors()

    if user_id not in known_visitors:
        lang = user.language_code or "en"
        welcome_msg = WELCOME_MESSAGES.get(lang, WELCOME_MESSAGES["default"])
        await update.message.reply_text(welcome_msg)
        known_visitors.add(user_id)
        save_known_visitors(known_visitors)

    summary = summarize_with_deepseek(text)

    message_to_owner = (
        f"📩 New message from @{user.username or user.first_name} (ID: {user.id})\n"
        f"📝 {text}\n\n"
        f"📌 Summary:\n{summary}"
    )
    await context.bot.send_message(chat_id=OWNER_ID, text=message_to_owner)

# ========== 群聊关键词监听 ==========
KEYWORDS = ["合租", "上车", "拼车", "出", "会员", "共享", "账号", "Netflix", "YouTube", "Apple Music", "iCloud", "Spotify"]

async def handle_group_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if any(kw.lower() in message.text.lower() for kw in KEYWORDS):
        group_name = update.effective_chat.title
        sender = message.from_user.full_name
        alert = (
            f"🚨 Keywords Mention！\n"
            f"👥 Cluster：{group_name}\n"
            f"🙋 USER：{sender}\n"
            f"💬 Content：{message.text}"
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=alert)

# ========== /start 命令 ==========
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = WELCOME_MESSAGES["en"]
    await update.message.reply_text(welcome_msg)

# ========== Flask 保活 ==========
web = Flask('')

@web.route('/')
def home():
    return "I'm alive!"

def run_web():
    web.run(host='0.0.0.0', port=10000)

# ========== 主函数 ==========
if __name__ == "__main__":
    # 启动 Flask Web 保活线程
    Thread(target=run_web).start()

    # 启动 Telegram Bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_keywords))

    logger.info("🤖 Bot is running...")
    app.run_polling()
