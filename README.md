# 群組摘要王 v2

群組摘要王 v2 是一款使用 FastAPI、LINE Messaging API 和 Google Generative AI，來為 LINE 群組的訊息進行摘要的開源專案。

> 點子來自：「[如何開發一個「LINE Bot 群組聊天摘要生成器](https://engineering.linecorp.com/zh-hant/blog/linebot-chatgpt)」

## 功能

- 接收 LINE 群組中的訊息。
- 透過命令清空對話歷史紀錄。
- 透過命令產生訊息的摘要。

## 開始使用

### 環境變數

在開始之前，您需要設定以下環境變數：

- `LINE_CHANNEL_SECRET`: 您的 LINE Bot Channel 密鑰
- `LINE_CHANNEL_ACCESS_TOKEN`: 您的 LINE Bot Channel 令牌
- `FIREBASE_URL`: 您的 Firebase 資料庫 URL
  - Example: https://OOOXXX.firebaseio.com/
- `GEMINI_API_KEY`: 您的 Gemini API 金鑰

如果您不在生產環境，請使用 `.env` 檔案來設定這些變數。

## 使用方式

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

```
git clone https://github.com/louis70109/linebot-gemini-summarize.git

cd linebot-gemini-summarize/

gcloud run deploy my-linebot-summarize --source .
```

## Q&A

> 遇到 AttributeError: type object 'MethodOptions' has no attribute 'RegisterExtension'

在此專案中有可能是套件相依過程有本版比較舊，因此建議使用 venv 之類的虛擬環境，重新安裝套件

```
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

> 部屬上 GCP 遇到 container 權限問題？

```
gcloud auth configure-docker # Y
```

## 授權

MIT
