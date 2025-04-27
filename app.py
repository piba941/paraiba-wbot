from flask import Flask, request, jsonify
from models import db, Order
import os
from utils import parse_xml_and_update_db
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['VERIFY_TOKEN'] = os.getenv('VERIFY_TOKEN')
app.config['ACCESS_TOKEN'] = os.getenv('ACCESS_TOKEN')

db.init_app(app)

@app.route('/')
def home():
    return "WhatsApp Bot is Running!"



@app.route('/webhook', methods=['POST', "GET"])
def webhook():

    VERIFY_TOKEN = app.config['VERIFY_TOKEN']

    if request.method == 'GET':
        # Webhook verification
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        mode = request.args.get('hub.mode')

        if mode and verify_token:
            print(verify_token, VERIFY_TOKEN)
            if verify_token == VERIFY_TOKEN:
                print('WEBHOOK_VERIFIED')
                return challenge, 200
            else:
                return 'Verification token mismatch', 403
        return 'Missing token', 400

    if request.method == 'POST':
        data = request.get_json()
        print('Received webhook:', data)

        # Extract the message from customer
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            customer_number = message['from']  # Phone number of sender
            text = message['text']['body'].strip()  # Text message they sent

            # Check if the message starts with 'status '
            if text.lower().startswith('status'):
                parts = text.split()
                if len(parts) >= 2:
                    order_no = parts[1]

                    # Look up order in database
                    order = Order.query.filter_by(order_no=order_no).first()
                    if order:
                        response_text = f"Hi {order.cust_first_name}, your order #{order_no} is currently '{order.order_status}'."
                    else:
                        response_text = f"Sorry, no order found with number {order_no}."

                    # Now, send a reply to customer
                    send_whatsapp_message(customer_number, response_text)

        except Exception as e:
            print(f"Error handling webhook: {e}")

        return jsonify({"status": "received"}), 200


def send_whatsapp_message(to_number, message):
    import requests

    url = 'https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages'
    headers = {
        'Authorization': f'Bearer YOUR_ACCESS_TOKEN',
        'Content-Type': 'application/json'
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': to_number,
        'type': 'text',
        'text': {
            'body': message
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print('Sent response:', response.status_code, response.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
