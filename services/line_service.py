from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from config import Config
# from app import db
from extensions import db

from models.user import User

# 初始化 LINE API 元件
line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

def get_handler():
    """取得 WebhookHandler（給 webhook.py 用）"""
    return handler

def ensure_user_registered(line_user_id):
    """確認用戶是否存在，若無則建立"""
    user = User.query.filter_by(line_user_id=line_user_id).first()
    if user:
        return user

    try:
        profile = line_bot_api.get_profile(line_user_id)
        display_name = profile.display_name
    except:
        display_name = "LINE User"

    user = User(line_user_id=line_user_id, name=display_name)
    db.session.add(user)
    db.session.commit()
    return user

def reply_to_user(reply_token, message):
    """發送簡單文字回覆給用戶"""
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=message)
    )
