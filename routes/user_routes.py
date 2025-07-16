from flask import Blueprint, request, jsonify
# from app import db
from extensions import db
from models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register_user():
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


@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [
        {"user_id": user.user_id, "line_user_id": user.line_user_id, "name": user.name}
        for user in users
    ]
    return jsonify({"users": user_list})
