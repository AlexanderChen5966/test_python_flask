from flask import Blueprint, request, jsonify
# from app import db
from extensions import db

from models.user import User
from models.line_reply import LineReply

line_reply_bp = Blueprint('line_reply', __name__)

@line_reply_bp.route('/line_reply', methods=['POST'])
def line_reply():
    data = request.get_json()
    user_id = data.get('user_id')
    reply_message = data.get('reply_message')

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    reply = LineReply(user_id=user_id, reply_message=reply_message)
    db.session.add(reply)
    db.session.commit()

    return jsonify({"message": "Reply sent successfully!"})
