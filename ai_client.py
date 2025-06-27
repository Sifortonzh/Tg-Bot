import os, requests

API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("OPENAI_API_KEY")

def summarize_message(user_input):
    messages = [{"role": "user", "content": f"请总结以下内容：{user_input}"}]
    res = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "deepseek-chat", "messages": messages}
    )
    return res.json()["choices"][0]["message"]["content"]
