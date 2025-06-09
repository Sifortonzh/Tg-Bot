import os
import json
import logging
import requests
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
                {"role": "system", "content": "你是一个帮我总结访客消息的AI助理，请用一句话概括他们想表达的核心内容。"},
                {"role": "user", "content": text}
            ],
            "temperature": 0.5
        }
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return "Summary unavailable."

# ========== 关键词监听 ==========
KEYWORDS = ["合租", "上车", "Netflix", "拼车", "Apple Music", "出车", "iCloud", "会员", "共享"]

# ========== 私聊消息处理 ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id

    if user_id == OWNER_ID:
        return

    known_visitors = load_known_visitors()

    if user_id not in known_visitors:
        welcome_msg = (
            "Hey there! 👋\n"
            "I'm not the boss — just the intern.\n"
            "Drop your message here and I’ll make sure it reaches the top desk. ☕"
        )
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
async def handle_group_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if any(kw.lower() in message.text.lower() for kw in KEYWORDS):
        group_name = update.effective_chat.title
        sender = message.from_user.full_name
        alert = (
            f"🚨 关键词触发！\n"
            f"👥 群组：{group_name}\n"
            f"🙋 用户：{sender}\n"
            f"💬 内容：{message.text}"
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=alert)

# ========== /start 命令 ==========
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "Hey there! 👋\n"
        "I'm not the boss — just the intern.\n"
        "Drop your message here and I’ll make sure it reaches the top desk. ☕"
    )
    await update.message.reply_text(welcome_msg)

# ========== 主函数 ==========
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_keywords))

    logger.info("🤖 Bot is now running...")
    app.run_polling()
