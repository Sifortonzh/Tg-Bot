from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from ai_client import summarize_message
from visitor import is_known, save_visitor
from monitor import check_keywords
import os

OWNER_ID = int(os.getenv("OWNER_ID"))
app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

async def forward_and_summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = msg.text
    sender = msg.from_user

    summary = summarize_message(text)
    forward_msg = f"📩 New message from @{sender.username or sender.id}\n📝 {text}\n📌 Summary:\n{summary}"
    await context.bot.send_message(chat_id=OWNER_ID, text=forward_msg)

    if not is_known(sender.id):
        await msg.reply_text("欢迎使用，请直接留言，我会帮你转发给主人！")
        save_visitor(sender.id)

    if msg.chat.type in ["group", "supergroup"]:
        if found := check_keywords(text):
            notice = f"🚨关键词触发：{found}\n👤 @{sender.username}\n📢 {text}"
            await context.bot.send_message(chat_id=OWNER_ID, text=notice)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_and_summarize))
app.run_polling()
