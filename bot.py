import os
import logging
import collections
import openai
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# Keywords to watch (expanded list)
KEYWORDS = [
    "join", "YouTube", "Netflix", "shared", "vpn", "account", "login",
    "上车", "合租", "机场", "油管", "拼车", "共享", "subscribe", "subscription",
    "premium", "会员", "付费", "share", "sharing", "spotify", "disney+", "hbo"
]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)

# Statistics tracking
stats = {
    "total_messages": 0,
    "new_users": 0,
    "keyword_matches": collections.Counter(),
    "user_activity": collections.defaultdict(int),
    "first_seen": {}
}

# AI summarization with improved error handling
def ai_summarize(text, user):
    try:
        if LLM_PROVIDER == "deepseek":
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You summarize Telegram messages concisely. Focus on shared accounts, group buys, or suspicious activity."
                    },
                    {
                        "role": "user", 
                        "content": f"Message from {user}:\n{text}\n\nSummarize key points in 1-2 sentences:"
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 150
            }
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You summarize Telegram messages concisely. Focus on shared accounts, group buys, or suspicious activity."
                    },
                    {
                        "role": "user", 
                        "content": f"Message from {user}:\n{text}\n\nSummarize key points in 1-2 sentences:"
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )
            return response.choices[0].message["content"].strip()
    except Exception as e:
        logging.error(f"AI summarization failed: {str(e)}")
        return f"[Summary failed: Message contained sensitive keywords]"

# Enhanced greeting for new users
def greet_user(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        stats["new_users"] += 1
        stats["first_seen"][member.id] = datetime.now().isoformat()
        
        welcome_msg = (
            f"👋 欢迎 {member.full_name} 加入群组！\n\n"
            "请仔细阅读群规：\n"
            "1. 禁止广告和 spam\n"
            "2. 合租信息请私聊管理员\n"
            "3. 保持友好交流\n\n"
            "需要帮助请耐心等待管理员回复~"
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_msg,
            reply_to_message_id=update.message.message_id
        )
        
        # Notify admin
        admin_msg = f"🆕 新成员加入: {member.full_name} (@{member.username or 'N/A'})"
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)

# Improved keyword monitoring with context
def keyword_listener(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.effective_user
    user_name = user.full_name
    user_id = user.id
    
    if not text:
        return
        
    stats["total_messages"] += 1
    stats["user_activity"][user_id] += 1
    
    # Check for keywords
    matched_keywords = [kw for kw in KEYWORDS if kw.lower() in text.lower()]
    
    if matched_keywords:
        for kw in matched_keywords:
            stats["keyword_matches"][kw] += 1
            
        summary = ai_summarize(text, user_name)
        message = (
            f"⚠️ *关键词警报* ⚠️\n"
            f"用户: {user_name} (ID: {user_id})\n"
            f"关键词: {', '.join(matched_keywords)}\n"
            f"摘要: {summary}\n\n"
            f"原始消息: {text[:200]}..."
        )
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

# Enhanced weekly report with more stats
def weekly_report(context: CallbackContext):
    try:
        # Calculate active users
        active_users = len([uid for uid, count in stats["user_activity"].items() if count >= 3])
        
        # Get top keywords
        top_keywords = stats["keyword_matches"].most_common(5)
        
        # Get new users this week
        new_users = stats["new_users"]
        stats["new_users"] = 0  # Reset for new week
        
        report = (
            "📊 *每周统计报告* 📊\n\n"
            f"📨 总消息数: {stats['total_messages']}\n"
            f"👥 新成员: {new_users}\n"
            f"🔥 活跃用户(3+消息): {active_users}\n\n"
            "🔍 热门关键词:\n"
        )
        
        for kw, count in top_keywords:
            report += f"- {kw}: {count}次\n"
            
        report += "\n📅 报告生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M")
        
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=report,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logging.error(f"Failed to generate weekly report: {str(e)}")

# Admin command to get stats
def stats_command(update: Update, context: CallbackContext):
    if str(update.effective_user.id) != ADMIN_CHAT_ID:
        update.message.reply_text("❌ 仅管理员可使用此命令")
        return
        
    active_users = len([uid for uid, count in stats["user_activity"].items() if count >= 3])
    update.message.reply_text(
        f"📊 实时统计:\n"
        f"总消息: {stats['total_messages']}\n"
        f"活跃用户: {active_users}\n"
        f"关键词匹配: {sum(stats['keyword_matches'].values())}次",
        parse_mode="Markdown"
    )

# Main function with error handling
def main():
    try:
        # Create logs directory if not exists
        os.makedirs("logs", exist_ok=True)
        
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Handlers
        dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_user))
        dp.add_handler(MessageHandler(Filters.text & Filters.group, keyword_listener))
        dp.add_handler(CommandHandler("stats", stats_command))
        
        # Scheduler for weekly report (every Monday at 9AM)
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            lambda: weekly_report(dp),
            trigger="cron",
            day_of_week="mon",
            hour=9,
            minute=0
        )
        scheduler.start()
        
        logging.info("Bot is running...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logging.critical(f"Bot crashed: {str(e)}")
        if ADMIN_CHAT_ID:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": ADMIN_CHAT_ID,
                    "text": f"🚨 Bot crashed: {str(e)}"
                }
            )

if __name__ == "__main__":
    main()