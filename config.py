import os
from dotenv import load_dotenv

# 載入 .env 設定
load_dotenv()

class Config:
    # 資料庫設定
    SQLALCHEMY_DATABASE_URI = os.getenv('POSTGRES_PUBLIC_URL')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LINE Bot 設定
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
