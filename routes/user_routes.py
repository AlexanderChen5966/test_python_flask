from flask import Blueprint, request, jsonify
# from app import db
from extensions import db
from models.user import User

user_bp = Blueprint('user', __name__)

# 註冊使用者 API
@user_bp.route('/register', methods=['POST'])
def register_user():
    # """
    # Register a new LINE user
    # ---
    # parameters:
    #   - name: line_user_id
    #     in: json
    #     type: string
    #     required: true
    #     description: LINE user ID
    #   - name: name
    #     in: json
    #     type: string
    #     required: true
    #     description: Name of the user
    # responses:
    #   200:
    #     description: User registration result
    #     schema:
    #       type: object
    #       properties:
    #         message:
    #           type: string
    # """
    data = request.get_json()
    line_user_id = data.get('line_user_id')
    name = data.get('name')

    if not line_user_id or not name:
        return jsonify({"message": "Missing line_user_id or name"}), 400

    existing_user = User.query.filter_by(line_user_id=line_user_id).first()
    if existing_user:
        return jsonify({"message": "User already registered"}), 200

    new_user = User(line_user_id=line_user_id, name=name)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# 查詢所有用戶的 API
@user_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get a list of all registered users
    ---
    responses:
      200:
        description: A list of all users in the system
        schema:
          type: object
          properties:
            users:
              type: array
              items:
                type: object
                properties:
                  user_id:
                    type: integer
                    description: User's unique ID
                  line_user_id:
                    type: string
                    description: User's LINE user ID
                  name:
                    type: string
                    description: User's name
    """
    users = User.query.all()
    user_list = [
        {"user_id": user.user_id, "line_user_id": user.line_user_id, "name": user.name}
        for user in users
    ]
    return jsonify({"users": user_list})
