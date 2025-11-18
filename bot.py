from flask import Flask, request
import os
import requests
import openai
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv('FB_PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('FB_VERIFY_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

# للتحقق من Webhook
@app.route('/webhook', methods=['GET'])
def verify():
    token_sent = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token_sent == VERIFY_TOKEN:
        return challenge
    return 'Invalid verification token'

# استقبال الرسائل
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'entry' in data:
        for entry in data['entry']:
            if 'messaging' in entry:
                for messaging_event in entry['messaging']:
                    if 'message' in messaging_event and 'text' in messaging_event['message']:
                        sender_id = messaging_event['sender']['id']
                        message_text = messaging_event['message']['text']

                        # ارسال السؤال لـ OpenAI API
                        response = openai.ChatCompletion.create(
                            model='gpt-3.5-turbo',
                            messages=[{'role': 'user', 'content': message_text}]
                        )
                        answer = response['choices'][0]['message']['content']

                        # ارسال الرد للمستخدم
                        send_message(sender_id, answer)
    return 'ok', 200

# دالة ارسال الرسائل للفيسبوك
def send_message(recipient_id, message_text):
    url = f'https://graph.facebook.com/v16.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(port=5000, debug=True)