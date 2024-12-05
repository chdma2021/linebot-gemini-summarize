import logging
import os
import sys
import requests
import json

from fastapi import FastAPI, HTTPException, Request
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
import google.generativeai as genai
from firebase import firebase

##
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
##

logging.basicConfig(level=os.getenv('LOG', 'WARNING'))
logger = logging.getLogger(__file__)

from flask import Flask, request
app = Flask(__name__)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
logging.info('channel_secret'+channel_secret)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
logging.info('channel_access_token'+channel_access_token)

##
# Channel Access Token
line_bot_api = LineBotApi('4LzDH06MaxmzIjRhO1Ol0c3PACVhY6uKB70ivR27WzGMnZpedIEHUOwLEOFFCbBbPCSpp7KB3+KVinTRwXguF4+eRnSaUMJ41Mxz7l5PbQbT3Ba/vdHIBtKGHR1Y3ar0mnVABvTcGqNFUMU/jTynRgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('a0b1901302e0d032af19bec7053e6e72')
##

if channel_secret is None:
    logging.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
    
if channel_access_token is None:
    logging.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

configuration = Configuration(
    access_token=channel_access_token
)

async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)


firebase_url = os.getenv('FIREBASE_URL')
gemini_key = os.getenv('GEMINI_API_KEY')


# Initialize the Gemini Pro API
genai.configure(api_key=gemini_key)

@app.get("/")
def home():
    return '歡迎來到中華數位行銷推廣協會'

@app.get("/health")
def health():
    return '我還活著喔'

def ai_message(question):
  prompt = question
  logging.info('question : '+question)
  logging.info('prompt : '+prompt)
  system_instructions = '你是個行銷專家'
  model = 'gemini-1.5-flash'
  temperature = 2

  if model == 'gemini-1.0-pro' and system_instructions is not None:
    system_instructions = None
    print('\x1b[31m(WARNING: System instructions ignored, gemini-1.0-pro does not support system instructions)\x1b[0m')

  if model == 'gemini-1.0-pro' and temperature > 1:
    temperature = 1
    print('\x1b[34m(INFO: Temperature set to 1, gemini-1.0-pro does not support temperature > 1)\x1b[0m')

  if system_instructions == '':
    system_instructions = None

  genai.configure(api_key=gemini_key)
  model = genai.GenerativeModel(model, system_instruction=system_instructions)
  config = genai.GenerationConfig(temperature=temperature)
  response = model.generate_content(contents=[prompt], generation_config=config)

  logging.info('response'+response.text)
  # print('response'+response.text)
  return response.text

@app.route('/chdma/<query>', methods=['GET'])
def chdma(query):
  return ai_message(query)
    
# endpoint for searching the web
@app.route('/search/<query>', methods=['GET'])
def serpapi_search(query):
    print(f'Searching the web for "{query}"')
    logging.info('Searching the web for ='+query)
    search_url = "https://serpapi.genai-pic.com/search"  # self hosted serpapi wrapper
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    response = requests.get(search_url, params=params, headers=headers)

    if response.status_code == 200:
        results = response.json()
        return results
    else:
        return jsonify({"error": "Failed to fetch results"}), response.status_code

@app.post("/webhooks/line")
def handle_callback(request: Request):
    signature = request.headers['X-Line-Signature']
    logging.info('signature ='+signature)
    # get request body as text
    body = request.body()
    body = body.decode()
    logging.info('body ='+body)
    
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        logging.info(event)
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue
        text = event.message.text
        user_id = event.source.user_id

        msg_type = event.message.type
        fdb = firebase.FirebaseApplication(firebase_url, None)
        if event.source.type == 'group':
            user_chat_path = f'chat/{event.source.group_id}'
        else:
            user_chat_path = f'chat/{user_id}'
            chat_state_path = f'state/{user_id}'
        chatgpt = fdb.get(user_chat_path, None)

        if msg_type == 'text':

            if chatgpt is None:
                messages = []
            else:
                messages = chatgpt
            logging.info('text ='+text)
            if text == '!清空':

                fdb.delete(user_chat_path, None)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='------對話歷史紀錄已經清空------')]
                    )
                )
            elif text == '!摘要':
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(
                    f'Summary the following message in Traditional Chinese by less 5 list points. \n{messages}')
                reply_msg = response.text
            else:
                model = genai.GenerativeModel('gemini-pro')
                messages.append({'role': 'user', 'parts': [text]})
                response = model.generate_content(messages)
                messages.append({'role': 'model', 'parts': [response.text]})
                # 更新firebase中的對話紀錄
                fdb.put_async(user_chat_path, None, messages)
                reply_msg = response.text
            
            logging.info('reply_msg ='+reply_msg)
            
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_msg)]
                ))

    return 'OK'

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    logging.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #message = TextSendMessage(text=event.message.text)
    #message = ai_message(query)
    message = '歡迎來到中華數位行銷推廣協會'
    logging.info("message : " + message)
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    app.run()
