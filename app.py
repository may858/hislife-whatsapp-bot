from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "hislifepeace123"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    print("Incoming message:")
    print(data)

    return "EVENT_RECEIVED", 200


@app.route("/")
def home():
    return "His Life and Peace Farms WhatsApp Bot is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
