from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import os

app = Flask(__name__)
swagger = Swagger(app)

# 環境變數設定
# DB_USER = os.getenv('DB_USER', 'root')
# DB_PASSWORD = os.getenv('DB_PASSWORD', '')
# DB_HOST = os.getenv('DB_HOST', 'localhost')
# DB_NAME = os.getenv('DB_NAME', 'flask_api')

# DB_USER = "root"
# DB_PASSWORD = "EkvRRMabtntpCBNAxYvmfHsQVhQCMapi"
# DB_HOST = "mysql.railway.internal"
# DB_NAME = "railway"

# DB_HOST=mysql.railway.internal
# DB_USER=root
# DB_PASSWORD=EkvRRMabtntpCBNAxYvmfHsQVhQCMapi
# DB_NAME=railway

# SQLAlchemy 資料庫 URI
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:EkvRRMabtntpCBNAxYvmfHsQVhQCMapi@switchyard.proxy.rlwy.net:47015/railway'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:EkvRRMabtntpCBNAxYvmfHsQVhQCMapi@mysql.railway.internal:3306/railway'

# mysql://root:EkvRRMabtntpCBNAxYvmfHsQVhQCMapi@mysql.railway.internal:3306/railway




app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 資料庫模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# 路由: GET users
@app.route('/users', methods=['GET'])
def get_users():
    """
    Get all users
    ---
    responses:
      200:
        description: A list of users
    """
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name} for u in users])

# 路由: POST user
@app.route('/users', methods=['POST'])
def add_user():
    """
    Add a new user
    ---
    parameters:
      - name: user
        in: body
        required: true
        schema:
          id: User
          required:
            - name
          properties:
            name:
              type: string
              example: Charlie
    responses:
      201:
        description: User created
    """
    data = request.get_json()
    user = User(name=data['name'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "name": user.name}), 201

# 主程式進入點
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 建立資料表
    app.run(host='0.0.0.0')




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
