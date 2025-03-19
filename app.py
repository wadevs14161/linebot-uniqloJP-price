import os
import sys
from flask import (Flask, render_template, request, abort)
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
    # Show template index.html
    return render_template('index.html')

@app.route("/calculator", methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        # Get input from form
        input1 = request.form['input1']
        input2 = request.form['input2']
        # Calculate
        result = int(input1) + int(input2)
        # Show result
        return render_template('calculator.html', result=result)
    return render_template('calculator.html')



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
    
    app.run(debug=True)
