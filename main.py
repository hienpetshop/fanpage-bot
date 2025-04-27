from flask import Flask, request
import openai
import os

app = Flask(__name__)

# Lấy API Key từ biến môi trường
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def verify():
    return "Webhook active", 200

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print(data)

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    user_message = messaging_event["message"]["text"]

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Bạn là trợ lý dễ thương, trả lời ngắn gọn."},
                            {"role": "user", "content": user_message}
                        ]
                    )

                    bot_reply = response["choices"][0]["message"]["content"]

                    print(f"User: {user_message}")
                    print(f"Bot: {bot_reply}")

    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
