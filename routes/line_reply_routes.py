from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from extensions import db

from models.user import User
from models.line_reply import LineReply

api = Namespace('LineReply', path='/api')

reply_model = api.model('LineReply', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'reply_message': fields.String(required=True, description='Message to reply to the user')
})

# 設計 POST /api/line_reply API
@api.route('/line_reply')
class LineReplyResource(Resource):
    @api.expect(reply_model)
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        reply_message = data.get('reply_message')

        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"message": "User not found"}, 404

        reply = LineReply(user_id=user_id, reply_message=reply_message)
        db.session.add(reply)
        db.session.commit()

        return {"message": "Reply sent successfully!"}
