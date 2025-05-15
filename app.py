from urllib.parse import urlparse
from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector
import os

app = Flask(__name__)
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# 資料庫連線
# def get_db():
#     conn = mysql.connector.connect(
#         host="localhost",  # MySQL 主機
#         user="root",  # MySQL 使用者名稱
#         password="password",  # MySQL 密碼
#         database="checkin_system"  # 資料庫名稱
#     )
#     return conn

def get_db():
    # 從環境變數中獲取資料庫連接字串
    db_url = os.getenv("MYSQL_URL")  # Railway 會自動設置此環境變數
    # 解析 DATABASE_URL 連接字串
    result = urlparse(db_url)

    conn = mysql.connector.connect(
        host=result.hostname,
        user=result.username,
        password=result.password,
        database=result.path[1:]  # 取得資料庫名稱 (去掉開頭的 `/`)
    )
    return conn


# 建立資料庫表格
@app.before_first_request
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INT AUTO_INCREMENT PRIMARY KEY,
                        line_user_id VARCHAR(255) NOT NULL UNIQUE,
                        name VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS checkins (
                        checkin_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        nfc_id VARCHAR(255),
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )''')

    conn.commit()
    cursor.close()
    conn.close()


# POST: 用戶打卡
@app.route('/api/checkin', methods=['POST'])
def checkin():
    data = request.json
    line_user_id = data.get('line_user_id')
    nfc_id = data.get('nfc_id')

    # 檢查用戶是否已存在
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE line_user_id = %s', (line_user_id,))
    user = cursor.fetchone()

    if user is None:
        # 新用戶，加入資料庫
        cursor.execute('INSERT INTO users (line_user_id) VALUES (%s)', (line_user_id,))
        conn.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user[0]

    # 儲存打卡紀錄
    cursor.execute('INSERT INTO checkins (user_id, nfc_id) VALUES (%s, %s)', (user_id, nfc_id))
    conn.commit()

    # 回傳訊息
    cursor.close()
    conn.close()
    return jsonify({"message": "你已成功打卡！"}), 200


# GET: 查詢打卡紀錄
@app.route('/api/checkins/<int:user_id>', methods=['GET'])
def get_checkins(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM checkins WHERE user_id = %s', (user_id,))
    checkins = cursor.fetchall()

    # 回傳查詢結果
    result = [{"checkin_id": checkin[0], "checkin_time": checkin[2], "nfc_id": checkin[3]} for checkin in checkins]
    cursor.close()
    conn.close()
    return jsonify(result), 200


# 使用 LINE 回應（模擬）
@app.route('/api/line_reply', methods=['POST'])
def line_reply():
    data = request.json
    line_user_id = data.get('line_user_id')
    message = "你已成功打卡！"
    # 這裡你會調用 LINE Messaging API 來回覆訊息
    # 例如使用 LINE SDK 發送訊息給用戶

    return jsonify({"message": "LINE reply sent successfully!"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
