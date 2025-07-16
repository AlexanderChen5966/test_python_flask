from flask import Blueprint, request, abort
from linebot import WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from config import Config
from extensions import db
from zoneinfo import ZoneInfo  # 如果你用 Python 3.9+

from models.user import User
from models.checkin import Checkin
from linebot import LineBotApi

webhook_bp = Blueprint('webhook', __name__)

line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

# 設置 LINE Webhook 路由
@webhook_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    if signature is None:
        abort(400)

    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception:
        abort(400)

    return "OK", 200

# 處理 LINE 訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_user_id = event.source.user_id
    user = User.query.filter_by(line_user_id=line_user_id).first()

    # 自動註冊用戶，如果用戶不存在就註冊
    if not user:
        try:
            profile = line_bot_api.get_profile(line_user_id)
            display_name = profile.display_name
        except:
            display_name = "LINE User"
        user = User(line_user_id=line_user_id, name=display_name)
        db.session.add(user)
        db.session.commit()

    user_id = user.user_id
    text = event.message.text.strip().lower()

    if text == "查詢":
        checkins = Checkin.query.filter_by(user_id=user_id).all()
        if checkins:
            # reply = "\n".join([c.checkin_time.strftime("%Y-%m-%d %H:%M:%S") for c in checkins])
            reply = "\n".join([
                c.checkin_time.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Taipei")).strftime(
                    "%Y-%m-%d %H:%M:%S")
                for c in checkins
            ])
            reply_text = f"📅 你的打卡紀錄：\n{reply}"
        else:
            reply_text = "❌ 你還沒有任何打卡紀錄喔。"

    elif text == "打卡":
        new_checkin = Checkin(user_id=user_id)
        db.session.add(new_checkin)
        db.session.commit()
        reply_text = "✅ 你已成功打卡！"

    else:
        reply_text = "請輸入『打卡』或『查詢』來使用服務！"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )
