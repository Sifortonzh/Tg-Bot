
# 🛎️ Slack-Style Telegram Assistant Bot

A lightweight, low-profile Telegram bot designed to quietly forward private messages and monitor group chats for keyword triggers. Runs on Render with Deepseek for AI-powered summaries. Slack intern vibes only. ☕

---

## 🧠 Features

- ✅ **Private message forwarding** – forwards visitor messages to you
- ✅ **Slack-style auto-reply** – greets new users with a friendly message
- ✅ **Deepseek-powered summaries** – summarizes each message with AI
- ✅ **Group keyword alerts** – monitors groups for words like "合租", "上车", "Netflix"
- ✅ **Render-compatible** – supports `run_polling` and Flask keepalive
- ✅ **UptimeRobot friendly** – stays awake with external pings
- ✅ **Multilingual welcome messages** – based on user language

---

## 📁 Project Structure

```
Tg-Bot/
├── main.py               # Main bot logic (polling + summary + alert)
├── known_visitors.json   # Stores users who already received welcome
├── README.md             # You're reading it!
├── .env (or use Render Env Settings)
└── requirements.txt      # Python dependencies
```

---

## ⚙️ Environment Variables

Create a `.env` file or set these in Render:

```env
BOT_TOKEN=your_telegram_bot_token
OWNER_ID=your_telegram_numeric_id
DEEPSEEK_API_KEY=your_deepseek_api_key
```

---

## 🚀 How to Run

### 🖥️ Local (for testing)

```bash
pip install -r requirements.txt
python main.py
```

### ☁️ Deploy on [Render](https://render.com)

1. Fork this repo
2. Connect it to Render as a Web Service
3. Set environment variables
4. Set port to `10000` (Flask keepalive server)
5. Enable auto-deploy from GitHub

---

## 🟢 Keepalive Setup with UptimeRobot

To prevent Render from sleeping:

1. Visit https://uptimerobot.com
2. Create an HTTPS monitor
3. Set ping URL as:

```
https://your-bot-name.onrender.com/
```

4. Set check interval to every 5 minutes

---

## 🧠 Group Keyword Monitoring

The bot scans all group messages for these software-sharing keywords:

```python
["合租", "上车", "Netflix", "拼车", "Apple Music", "出车", "iCloud", "会员", "共享"]
```

If triggered, it alerts the owner with:

- Group name
- Sender
- Original message

---

## 💬 Bot Personality

This bot is your loyal intern. Doesn’t talk much.  
Takes a message, nods, walks quietly to the boss’s desk and drops it off.  
Slack vibes only. ☕

---

## 📝 requirements.txt

```text
python-telegram-bot==20.7
Flask==2.3.3
requests
```

---

## 📎 Example Screenshot

_(Optional)_ Add a screenshot of the bot in action here:

```
📩 New message from @username (ID: 123456789)
📝 I’d like to join the Apple Music group.
📌 Summary:
User is asking to join a shared Apple Music group.
```

---

## ✅ Roadmap

- [x] Deepseek summary integration
- [x] UptimeRobot keepalive
- [x] Welcome message memory
- [ ] Claude/GPT switchable backend
- [ ] Command menu for bot settings
- [ ] Notion/Airtable message log

---

## 👨‍💻 Author

**Ryan**  
🔗 [avecrouge.com](https://avecrouge.com)  
🤖 Telegram Bot: [@avechat_bot](https://t.me/avechat_bot)
