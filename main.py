import os
import logging
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === 从环境变量中读取配置 ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# === 日志配置 ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === Flask 心跳服务 ===
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# 在后台线程启动 Flask
Thread(target=run_web).start()

# === 摘要函数 ===
def summarize_with_deepseek(text):
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个信息摘要助手"},
                {"role": "user", "content": f"请总结以下访客消息内容：\n{text}"}
            ]
        }
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[摘要失败]: {e}"

# === 处理访客消息 ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if user.id == OWNER_ID:
        return  # 不转发你自己的消息

    summary = summarize_with_deepseek(text)

    message_to_owner = (
        f"📩 新消息来自 @{user.username or user.first_name}（ID: {user.id}）\n"
        f"📝 内容：{text}\n\n"
        f"📌 摘要：\n{summary}"
    )

    await context.bot.send_message(chat_id=OWNER_ID, text=message_to_owner)

# === 启动 Telegram Bot ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot 正在运行...")
    app.run_polling()

KEYWORDS = [
    "合租", "上车", "拼车", "拼团", "分摊", "出车",
    "车位", "车主", "车队", "组团", "车坑",
    "长期车", "临时车", "接人", "缺人",
    "YouTube", "Netflix", "Spotify", "Apple Music",
    "iCloud", "阿里云盘", "百度网盘", "迅雷", "腾讯视频",
    "会员", "Premium", "账号", "共享", "车速"
]

async def handle_group_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_type = update.effective_chat.type
    text = message.text.lower()

    if chat_type in ["group", "supergroup"]:
        if any(keyword.lower() in text for keyword in KEYWORDS):
            alert = (
                f"🚨 软件合租关键词触发！\n"
                f"群名：{update.effective_chat.title}\n"
                f"发言人：{message.from_user.full_name}\n"
                f"内容：{message.text}"
            )
            await context.bot.send_message(chat_id=OWNER_ID, text=alert)
