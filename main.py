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
