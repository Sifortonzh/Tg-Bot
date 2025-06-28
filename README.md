# Slack-Style Telegram Bot 🤖

This is a Telegram bot with Slack-style interaction logic, built using Python.

## ✨ Features

1. **👋 Welcome New Users**  
   Greets new members who join the group.

2. **🔍 Keyword Monitoring**  
   Listens for keywords like `上车`, `YouTube`, `Netflix`, etc., in group messages.

3. **🧠 AI-Based Message Summary**  
   Forwards analyzed messages to admin (currently mocked, replace with real AI API).

4. **📊 Weekly Stats Report**  
   Automatically sends a weekly summary of keyword usage and message activity.

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/tg-bot-slack-style.git
cd tg-bot-slack-style
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup environment variables

Create a `.env` file or set environment variables:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_telegram_id
```

### 4. Run the bot

```bash
python bot.py
```

---

## 📁 Project Structure

```
tg-bot-slack-style/
├── bot.py                 # Main bot script
├── data/                  # Future data storage
├── logs/                  # Logs folder
├── scripts/               # Optional scripts
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```

---

## 📌 To Do

- [ ] Integrate with OpenAI for real AI message summarization
- [ ] Webhook deployment
- [ ] Command interface for admin

---

## 🛠 Tech Stack

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [APScheduler](https://apscheduler.readthedocs.io/en/latest/)
