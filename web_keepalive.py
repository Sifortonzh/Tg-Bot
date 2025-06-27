from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is alive."

if __name__ == "__main__":
    app.run(port=10000)
