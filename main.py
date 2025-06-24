import logging
import os
import sys
import requests
import json

#from fastapi import FastAPI, HTTPException, Request
##
#from flask import Flask, Request
from flask import render_template
#from flask import HTTPException
##
from flask import Flask, request

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
    InvalidSignatureError , LineBotApiError
)
from linebot.models import *
##

logging.basicConfig(level=os.getenv('LOG', 'WARNING'))
logger = logging.getLogger(__file__)

app = Flask(__name__)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
logging.info('channel_secret:'+channel_secret)
print('channel_secret:' + channel_secret)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
logging.info('channel_access_token:'+channel_access_token)
print('channel_access_token:'+channel_access_token)

##
# Channel Access Token
line_bot_api_key = os.getenv('LINE_BOT_API', None)
logging.info('line_bot_api_key:'+line_bot_api_key)
print('line_bot_api_key:'+line_bot_api_key)
line_bot_api = LineBotApi(line_bot_api_key)
# Channel Secret
handler = WebhookHandler(channel_secret)
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
#line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)


firebase_url = os.getenv('FIREBASE_URL')
#gemini_key = os.getenv('GEMINI_API_KEY')
## change api key for CHDMA
gemini_key = 'AIzaSyBNJncqirX0Cb-yGaYMhdfIU1K0IWBaYig'

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
  system_instructions = ""
  system_instructions += "中華數位行銷推廣協會 (CHDMA) 員工訓練資料：\n\n"
  system_instructions += "何為中華數位行銷推廣協會？\n\n"
  system_instructions += "中華數位行銷推廣協會 (https://chdma.org.tw/)，英文簡稱 CHDMA，是一個以非營利為目的之公益性社會團體，宗旨為促進數位行銷及相關領域之研究、發展、應用與交流。\n\n"
  system_instructions += "中華數位行銷推廣協會的聯絡人及聯絡方式？\n\n"
  system_instructions += "聯絡人：李孟峰\n"
  system_instructions += "電話：0911633190\n"
  system_instructions += "電子信箱：chdma2021@gmail.com\n"
  system_instructions += "地址：臺北市中山區南京東路二段 11 號 10 樓 B 室\n\n"
  system_instructions += "中華數位行銷推廣協會的入會資格及會員費用？\n\n"
  system_instructions += "凡贊同本會宗旨年滿18歲之個人、大專院校學生（碩士在職專班除外）、及團體均得填具入會申請書，經理事會審查通過後入會。凡同本會宗旨且贊助本會經費、資源之個人或團體，填具入會申請書，經理事會審查通過後，為贊助會員。\n\n"
  system_instructions += "會員費用：\n"
  system_instructions += "入會費：個人會員新臺幣壹仟元、團體會員新臺幣伍仟元、學生會員免入會費。\n"
  system_instructions += "常年費：個人會員新臺幣壹仟元、團體會員新臺幣伍仟元、學生會員新臺幣伍佰元。\n\n"
  system_instructions += "中華數位行銷推廣協會的行銷口號？\n\n"
  system_instructions += "* 數位轉型，驅動未來。\n"
  system_instructions += "* 科技賦能，行銷升級。\n"
  system_instructions += "* 連結全球，實體蛻變。\n"
  system_instructions += "* 培育人才，共創數位新局。\n\n"
  system_instructions += "中華數位行銷推廣協會的協會宗旨、任務及使命？\n\n"
  system_instructions += "* 宗旨：本會以非營利為目的之公益性社會團體，以促進數位行銷及相關領域之研究、發展、應用與交流為宗旨。\n"
  system_instructions += "* 任務：\n"
  system_instructions += "* 提升實體企業科技應用能力\n"
  system_instructions += "* 接軌全球數位行銷科技資源\n"
  system_instructions += "* 舉辦與數位行銷相關之學術會議、研習、講習、訓練、討論、訪問、觀摩等\n"
  system_instructions += "* 推動實體數位行銷轉型\n"
  system_instructions += "* 培育數位行銷轉型人才\n"
  system_instructions += "* 其他有關數位行銷之研究發展事項\n"
  system_instructions += "* 使命：培育具備國際視野與實務能力的數位行銷人才，為台灣數位經濟注入新動能。\n\n"
  system_instructions += "中華數位行銷推廣協會的願景及預期達到目標？\n\n"
  system_instructions += "* 願景：成為台灣數位行銷人才的搖籃，提供優質的學習資源與發展平台，讓每位學員都能成為數位時代的佼佼者。\n"
  system_instructions += "* 預期達到目標：\n"
  system_instructions += "* 透過數位行銷推動社會公益，促進社會發展。\n"
  system_instructions += "* 鼓勵數位行銷創新，培育新一代的數位行銷領袖。\n"
  system_instructions += "* 協助中小企業進行數位轉型，促進地方經濟發展。\n\n"
  system_instructions += "關於 CHDMA 未來發展及挑戰的思考方向：\n\n"
  system_instructions += "* 提升協會知名度：舉辦大型的數位行銷競賽、與知名品牌合作、推出線上學習平台等。\n"
  system_instructions += "* 開發新服務滿足會員需求：提供一對一的諮詢服務、建立會員交流平台、開發數位行銷工具等。\n"
  system_instructions += "* 利用 AI 技術提升服務品質：利用 AI 進行數據分析、提供個人化學習建議、開發 AI 輔助的數位行銷工具。\n"
  system_instructions += "* 合作單位：政府單位、學術機構、企業、其他相關協會等。\n"
  system_instructions += "* 未來最大挑戰：跟上快速變化的數位行銷技術、培育符合未來需求的數位行銷人才。\n"
  system_instructions += "* 吸引年輕人加入：舉辦學生專屬活動、提供獎學金、與學校合作開設課程等。\n"
  system_instructions += "* 確保人才符合產業需求：與企業合作、邀請業界專家授課，讓課程內容更貼近產業實務。\n"
  system_instructions += "* 未來發展方向：拓展國際合作、深化 AI 在數位行銷的應用、針對特定產業提供更專業的服務。\n"
  system_instructions += "官方網站：https://chdma.org/"
  system_instructions += "加入 Line 官方好友的連結 https://lin.ee/Vn0Zfhd 可以即時獲得更多訊息"
  system_instructions += "Youtube 官方頻道：https://www.youtube.com/channel/UCT6xgBaEd-NTN76JMwFu3Cg ，或者搜尋 chdma2021，有更多免費的協會訊息與大師開講"
  system_instructions += "Facebook 官方粉絲專頁：https://www.facebook.com/CHDMA.TW，或者搜尋 chdma2021"
  system_instructions += "Instgram：https://www.instagram.com/chdma_2021?igsh=aDloOTdqcHh2M，或者搜尋 chdma2021"  
  system_instructions += "台北大學數位行銷學士學位學程：https://www.dma.ntpu.edu.tw/"
  system_instructions += "中華數位行銷推廣協會：https://chdma.org.tw"  

  #print(system_instructions)
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

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    logging.info('Hello [/callback] I am come in')
    print('Hello [/callback] I am come in')
    
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
    logging.info('Loggin : Hello [handle_message] I am come in')
    print('Print : Hello [handle_message] I am come in')

    
    mtext = event.message.text
    ##
    logging.info('loggin : event.message.text : ' + event.message.text)
    print('Print :event.message.text : ' + event.message.text)
    ##
    fdb = firebase.FirebaseApplication('https://chdma-firebase-linebot-default-rtdb.firebaseio.com', None)
    if event.source.type == 'group':
       group_id = event.source.groupid
       user_chat_path = f'chat/{group_id}'
       print('group_id = ' + group_id)
       fdb.put_async(user_chat_path, 'groupInfo', 'group_id =  ' + group_id)
    else:
       user_id = event.source.user_id
       user_chat_path = f'chat/{user_id}'
       print('user_id = ' + user_id)
       fdb.put_async(user_chat_path, 'userInfo', 'user_id =  ' + user_id)
       #先取得使用者 Display Name (也就是顯示的名稱)
    try:
       #先取得使用者 Display Name (也就是顯示的名稱)
       profile = line_bot_api.get_profile(user_id)
       if not profile.display_name.strip() == "":
           print('user display name = ' + profile.display_name) #記錄使用者名稱
           fdb.put_async(user_chat_path, 'userInfo', 'user display name = ' + profile.display_name)           
       if not profile.picture_url.strip() == "":
           print('user picture_url = ' + profile.picture_url) #大頭貼網址
           fdb.put_async(user_chat_path,  'userInfo', 'user picture_url = ' + profile.picture_url)                      
    except LineBotApiError as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error.message)
        print(e.error.details)        

    if mtext == '!清空':
       fdb.delete(user_chat_path, None)
       line_bot_api.reply_message(
            ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text='------對話歷史紀錄已經清空------')]
            )
        )
        fdb.put_async(user_chat_path, '------對話歷史紀錄已經清空------')
    else:
        responseMessage = ai_message(mtext)
        if not profile.display_name.strip() == "":
            responseMessage = "感謝 {display_name}, 您所提出的問題，以下是我的答覆，希望您能滿意\n \n {replyMessage}".format(display_name = profile.display_name, replyMessage = responseMessage)
            #responseMessage = '感謝 ' + profile.display_name + '您所提出的問題，以下是我的答覆，希望您能滿意\n'  + responseMessage
        else:
            responseMessage = ai_message(mtext)
        
        # 更新firebase中的對話紀錄
        fdb.put_async(user_chat_path, 'question:', mtext)
        fdb.put_async(user_chat_path, 'answer:', responseMessage)
    
        #message = '歡迎來到中華數位行銷推廣協會'
        #logging.info('Loggin : responseMessage : ' + responseMessage)
        #print('Print : responseMessage : ' + responseMessage)
    
        event.message.text = responseMessage
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    return 'OK'

if __name__ == "__main__":
    app.run()
