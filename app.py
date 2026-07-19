import os
import requests
from flask import Flask, request

from sales.conversation import handle_message
from sales.inventory import create_inventory_file
from sales.config import BUSINESS_WHATSAPP_NUMBER

app = Flask(__name__)

VERIFY_TOKEN = "hislifepeace123"

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# DEBUG
print("ACCESS_TOKEN loaded:", ACCESS_TOKEN is not None)
print("PHONE_NUMBER_ID:", PHONE_NUMBER_ID)

WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# Make sure the inventory CSV exists on the persistent disk on startup,
# same as SalesApp.build() did for the Kivy app.
create_inventory_file()


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

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages")

        if messages:
            message = messages[0]
            sender_number = message.get("from")
            message_text = message.get("text", {}).get("body", "")

            print(f"From: {sender_number} | Message: {message_text}")

            reply_text, admin_notification = handle_message(sender_number, message_text)

            if reply_text:
                send_whatsapp_message(sender_number, reply_text)

            if admin_notification:
                send_whatsapp_message(BUSINESS_WHATSAPP_NUMBER, admin_notification)

    except (IndexError, KeyError, AttributeError) as e:
        print(f"Error parsing webhook payload: {e}")

    return "EVENT_RECEIVED", 200


def send_whatsapp_message(to_number, message_text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_text
        },
    }

    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        print(f"WhatsApp API response: {response.status_code} {response.text}")
    except requests.RequestException as e:
        print(f"Error sending WhatsApp message: {e}")


@app.route("/")
def home():
    return "His Life and Peace Farms WhatsApp Bot (with Sales Management) is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
