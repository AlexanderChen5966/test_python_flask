from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from extensions import db
from models.user import User

api = Namespace('User', path='/api')

user_model = api.model('UserRegister', {
    'line_user_id': fields.String(required=True, description='LINE user ID'),
    'name': fields.String(required=True, description='User name')
})

# 註冊使用者 API
@api.route('/register')
class UserRegister(Resource):
    @api.expect(user_model)
    def post(self):
        data = request.get_json()
        line_user_id = data.get('line_user_id')
        name = data.get('name')

        if not line_user_id or not name:
            return {"message": "Missing line_user_id or name"}, 400

        existing_user = User.query.filter_by(line_user_id=line_user_id).first()
        if existing_user:
            return {"message": "User already registered"}, 200

        new_user = User(line_user_id=line_user_id, name=name)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User registered successfully"}, 201

# 查詢所有用戶的 API
@api.route('/users')
class UserList(Resource):
    def get(self):
        users = User.query.all()
        user_list = [
            {"user_id": user.user_id, "line_user_id": user.line_user_id, "name": user.name}
            for user in users
        ]
        return {"users": user_list}
