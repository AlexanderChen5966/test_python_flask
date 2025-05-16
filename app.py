import os
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage
from datetime import datetime
from dotenv import load_dotenv


# 初始化 Flask 應用
app = Flask(__name__)
load_dotenv()  # 會自動從根目錄的 .env 檔載入變數


# 設定資料庫配置（MySQL）
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_URI')  # 設定 MySQL 資料庫 URI（從 Railway 取得）
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:LepIwlpQcMsIqKKSMMrSbpSasaEDLywE@caboose.proxy.rlwy.net:56460/railway"
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:LepIwlpQcMsIqKKSMMrSbpSasaEDLywE@caboose.proxy.rlwy.net:56460/railway'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_URL','MYSQL_PUBLIC_URL')


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SQLAlchemy 預設會嘗試使用 MySQLdb，但這個套件在 Windows 上很難安裝，建議改用 pymysql 或 mysqlclient（較難安裝）。
# 建議做法： pymysql
# 變 URI 格式，在前面加上 mysql+pymysql://
#如果你原本的 .env 是這樣：MYSQL_PUBLIC_URL=mysql://root:password@host:port/dbname
#要改成MYSQL_PUBLIC_URL=mysql+pymysql://root:password@host:port/dbname


db = SQLAlchemy(app)

# 設定 LINE API 的 Token 和 Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# 初始化 LINE Bot API 和 WebhookHandler
# line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
# handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化 Flasgger
swagger = Swagger(app)


# 定義資料庫模型

# 用戶資料表格
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    line_user_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# 打卡紀錄資料表格
class Checkin(db.Model):
    checkin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    checkin_time = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('checkins', lazy=True))


# LINE 回覆資料表格
class LineReply(db.Model):
    reply_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    reply_message = db.Column(db.Text, nullable=False)
    reply_time = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('line_replies', lazy=True))


# 設計 POST /api/checkin API
@app.route('/api/checkin', methods=['POST'])
def checkin():
    """
    User check-in API
    ---
    parameters:
      - name: line_user_id
        in: json
        type: string
        required: true
        description: LINE user ID
    responses:
      200:
        description: "Check-in successful"
        schema:
          type: object
          properties:
            message:
              type: string
              example: "You have successfully checked in!"
    """
    data = request.get_json()
    line_user_id = data.get('line_user_id')

    # 查找用戶
    user = User.query.filter_by(line_user_id=line_user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # 儲存打卡紀錄
    checkin = Checkin(user_id=user.user_id)
    db.session.add(checkin)
    db.session.commit()

    return jsonify({"message": "You have successfully checked in!"})


# 設計 GET /api/checkins/{user_id} API
@app.route('/api/checkins/<int:user_id>', methods=['GET'])
def get_checkins(user_id):
    """
    Get check-ins of a user
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: "User check-ins found"
        schema:
          type: object
          properties:
            checkins:
              type: array
              items:
                type: object
                properties:
                  checkin_id:
                    type: integer
                  checkin_time:
                    type: string
                    format: date-time
    """
    checkins = Checkin.query.filter_by(user_id=user_id).all()
    checkin_list = [
        {"checkin_id": checkin.checkin_id, "checkin_time": checkin.checkin_time.isoformat()}
        for checkin in checkins
    ]

    return jsonify({"checkins": checkin_list})


# 設計 POST /api/line_reply API
@app.route('/api/line_reply', methods=['POST'])
def line_reply():
    """
    Reply to a user in LINE
    ---
    parameters:
      - name: user_id
        in: json
        type: integer
        required: true
        description: User ID
      - name: reply_message
        in: json
        type: string
        required: true
        description: Message to reply to the user
    responses:
      200:
        description: "Reply sent successfully"
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Reply sent successfully!"
    """
    data = request.get_json()
    user_id = data.get('user_id')
    reply_message = data.get('reply_message')

    # 查找用戶
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # 儲存LINE回覆
    reply = LineReply(user_id=user_id, reply_message=reply_message)
    db.session.add(reply)
    db.session.commit()

    return jsonify({"message": "Reply sent successfully!"})


# 設置 LINE Webhook 路由
# @app.route("/callback", methods=["POST"])
# def callback():
#     # 確保是 LINE 發來的請求
#     if request.headers["X-Line-Signature"] is None:
#         abort(400)
#
#     body = request.get_data(as_text=True)
#     signature = request.headers["X-Line-Signature"]
#     handler.handle(body, signature)
#
#     return 'OK', 200


# 處理 LINE 訊息
# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     # 回覆用戶訊息
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextMessage(text='You have successfully checked in!')
#     )


# 啟動 Flask 應用
if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()  # 建立資料表
    # app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))





# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flasgger import Swagger
# import os
#
# app = Flask(__name__)
# swagger = Swagger(app)
#
# # 環境變數設定
# # DB_USER = os.getenv('DB_USER', 'root')
# # DB_PASSWORD = os.getenv('DB_PASSWORD', '')
# # DB_HOST = os.getenv('DB_HOST', 'localhost')
# # DB_NAME = os.getenv('DB_NAME', 'flask_api')
#
# # DB_USER = "root"
# # DB_PASSWORD = "EkvRRMabtntpCBNAxYvmfHsQVhQCMapi"
# # DB_HOST = "mysql.railway.internal"
# # DB_NAME = "railway"
#
# # DB_HOST=mysql.railway.internal
# # DB_USER=root
# # DB_PASSWORD=EkvRRMabtntpCBNAxYvmfHsQVhQCMapi
# # DB_NAME=railway
#
# # SQLAlchemy 資料庫 URI
# # app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:EkvRRMabtntpCBNAxYvmfHsQVhQCMapi@switchyard.proxy.rlwy.net:47015/railway'
# # app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:EkvRRMabtntpCBNAxYvmfHsQVhQCMapi@mysql.railway.internal:3306/railway'
#
# # mysql://root:EkvRRMabtntpCBNAxYvmfHsQVhQCMapi@mysql.railway.internal:3306/railway
#
#
# # DB_HOST=containers-xxxxx.railway.internal
# # DB_USER=your_user
# # DB_PASSWORD=your_password
# # DB_NAME=your_database
#
#
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db = SQLAlchemy(app)
#
# # 資料庫模型
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#
# # 路由: GET users
# @app.route('/users', methods=['GET'])
# def get_users():
#     """
#     Get all users
#     ---
#     responses:
#       200:
#         description: A list of users
#     """
#     users = User.query.all()
#     return jsonify([{"id": u.id, "name": u.name} for u in users])
#
# # 路由: POST user
# @app.route('/users', methods=['POST'])
# def add_user():
#     """
#     Add a new user
#     ---
#     parameters:
#       - name: user
#         in: body
#         required: true
#         schema:
#           id: User
#           required:
#             - name
#           properties:
#             name:
#               type: string
#               example: Charlie
#     responses:
#       201:
#         description: User created
#     """
#     data = request.get_json()
#     user = User(name=data['name'])
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"id": user.id, "name": user.name}), 201
#
# # 主程式進入點
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # 建立資料表
#     app.run(host='0.0.0.0')




# from flask import Flask, jsonify, request
# from flasgger import Swagger
#
# app = Flask(__name__)
# swagger = Swagger(app)
#
# # 假資料
# FAKE_DB = [
#     {"id": 1, "name": "Alice"},
#     {"id": 2, "name": "Bob"}
# ]
#
# @app.route('/users', methods=['GET'])
# def get_users():
#     """
#     Get all users
#     ---
#     responses:
#       200:
#         description: A list of users
#         examples:
#           application/json: [{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]
#     """
#     return jsonify(FAKE_DB)
#
# @app.route('/users', methods=['POST'])
# def add_user():
#     """
#     Add a new user
#     ---
#     parameters:
#       - name: user
#         in: body
#         required: true
#         schema:
#           id: User
#           required:
#             - name
#           properties:
#             name:
#               type: string
#               description: The user's name
#               example: Charlie
#     responses:
#       201:
#         description: User created
#         examples:
#           application/json: {"id":3,"name":"Charlie"}
#     """
#     data = request.get_json()
#     new_user = {
#         "id": len(FAKE_DB) + 1,
#         "name": data["name"]
#     }
#     FAKE_DB.append(new_user)
#     return jsonify(new_user), 201
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0')
