from flask import Flask, request
import os
import requests

try:
    import openai
except ImportError:
    raise ImportError("The 'openai' package is not installed. Please install it with 'pip install openai'")

app = Flask(__name__)

VERIFY_TOKEN = "hien6985"  # Token bạn điền trong Facebook
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")  # Thêm biến môi trường này!

# Initialize OpenAI client safely
if os.getenv("OPENAI_API_KEY"):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    raise EnvironmentError("OPENAI_API_KEY is not set in environment variables.")

@app.route("/", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge, 200
    else:
        return "Verification token mismatch", 403

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print(data)

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    user_message = messaging_event["message"].get("text", "")

                    if user_message:  # Ensure user_message is not empty
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Bạn là trợ lý dễ thương, trả lời ngắn gọn."},
                                {"role": "user", "content": user_message}
                            ]
                        )

                        bot_reply = response.choices[0].message.content

                        send_message(sender_id, bot_reply)

    return "EVENT_RECEIVED", 200

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
