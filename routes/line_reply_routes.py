from flask import Blueprint, request, jsonify
# from app import db
from extensions import db

from models.user import User
from models.line_reply import LineReply

line_reply_bp = Blueprint('line_reply', __name__)

# 設計 POST /api/line_reply API
@line_reply_bp.route('/line_reply', methods=['POST'])
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

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    reply = LineReply(user_id=user_id, reply_message=reply_message)
    db.session.add(reply)
    db.session.commit()

    return jsonify({"message": "Reply sent successfully!"})
