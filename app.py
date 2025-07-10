import os
import sys
from flask import (Flask, render_template, request, abort, jsonify)
from flask_cors import CORS
from linebot.v3 import (
    WebhookParser,
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage
)

from crawl import product_crawl
from reply import reply_message


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

parser = WebhookParser(channel_secret)
handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)


@app.route('/', methods=['GET', 'POST'])
def index():
    return '''
    <html>
        <head>
            <title>Uniqlo Japan Price Finder</title>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 2rem;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                }
                h1 {
                    font-size: 3em;
                    margin-bottom: 1rem;
                }
                .subtitle {
                    font-size: 1.2em;
                    margin-bottom: 2rem;
                    opacity: 0.9;
                }
                .button {
                    display: inline-block;
                    padding: 15px 30px;
                    margin: 10px;
                    background: rgba(255, 255, 255, 0.2);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 10px;
                    color: white;
                    text-decoration: none;
                    font-size: 1.1em;
                    transition: all 0.3s ease;
                }
                .button:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: translateY(-2px);
                }
                .flag {
                    font-size: 2em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>UNIQLO 日本 找價格</h1>
                <p class="subtitle">Line Bot Server & Web Interface</p>
                <div>
                    <a href="http://localhost:5173" class="button" target="_blank">
                        🌐 Open Web Interface
                    </a>
                    <div style="margin-top: 1rem; font-size: 0.9em; opacity: 0.8;">
                        <p>Web Interface: Product search with history</p>
                        <p>Line Bot: Webhook endpoint for Line messaging</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    '''



@app.route("/find_product", methods=['POST'])
def find_product():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    message_input = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if message_input == "1":
            print("User ask for example!")
            img_url = "https://i.imgur.com/HLw9BhO.jpg"
            reply = ImageMessage(original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[reply]))
        else:
            print("Start crawling!")
            result = product_crawl(message_input)
            reply_message(result, event, line_bot_api)
                    
    return 'OK'

@app.route("/api/search", methods=['POST'])
def api_search():
    """API endpoint for product search from React frontend"""
    try:
        data = request.get_json()
        product_id = data.get('product_id', '').strip()
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        print(f"API Search for product ID: {product_id}")
        result = product_crawl(product_id)
        
        if result == -1:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# @handler.add(MessageEvent, message=ImageMessageContent)
# def message_image(event):
#     with ApiClient(configuration) as api_client:
#         print("User sent a image!")
#         line_bot_api = MessagingApi(api_client)
#         messageId = event.message.id
#         image_url = upload_image(channel_access_token, messageId)

#         result = analyze(image_url)

#         serial_number = ""
#         for line in result.read.blocks[0].lines:
#             if len(line.text) == 10:
#                 if line.text[-6:].isnumeric():
#                     serial_number = line.text[-6:]
#                     print("serial number : " + serial_number)

#         crawlResult = product_crawl(serial_number)
        
#         reply_message(crawlResult, event, line_bot_api)

#     return "OK"

if __name__ == '__main__':
    # Running on port 5000, let nginx (port 8080) to proxy to this port
    app.run(debug=True, host='0.0.0.0', port=5000)
