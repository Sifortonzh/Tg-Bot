# Slack-Style Telegram Bot 🤖

A friendly and intelligent Telegram bot designed to auto-greet new users, monitor shared-account keywords, summarize messages using OpenAI, and report weekly usage stats — all with a Slack-like experience.

---

## 🚀 Features

- 👋 Auto-greets new members with a welcome message
- 🔍 Monitors messages for keywords like `YouTube`, `Netflix`, `合租`, etc.
- 🧠 Summarizes messages using either **OpenAI** or **Deepseek** based on configuration
- 📊 Sends a weekly keyword and usage report to the admin
- 🕒 Optimized for Render deployment with **UptimeRobot** keep-alive

---

## 🧱 Project Structure

```
tg-bot/
├── bot.py               # Main bot script
├── requirements.txt     # Python dependencies
├── logs/                # Log output folder
├── data/                # Reserved for future data handling
└── README.md            # This file
```

---

## 🛠 Setup & Deployment

### 1. Prepare environment

Make sure you have Python 3.8+ and run:

```bash
pip install -r requirements.txt
```

### 2. Setup environment variables

Add the following variables in Render → Environment tab:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_personal_telegram_id

# Choose one of the following providers:
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key

# OR
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
```


Add the following variables in Render → Environment tab:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_personal_telegram_id
OPENAI_API_KEY=your_openai_api_key
```

### 3. Deploy to Render

- Create a new **Web Service**
- Connect your GitHub repo
- Set `Start Command` as:

```bash
python bot.py
```

### 4. Setup UptimeRobot (for keep-alive)

Use [https://uptimerobot.com/](https://uptimerobot.com/) to ping your Render URL every 5 minutes.

---

## 🧠 Extend This Bot

- Add commands like `/summary`, `/help`
- Switch to webhook + Flask for faster response
- Add SQLite or Supabase for persistent storage

---

## 📬 Author

Built with ❤️ by [Ryan](avecrouge.com)

MIT License.
