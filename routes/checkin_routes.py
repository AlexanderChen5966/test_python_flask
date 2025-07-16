from flask import Blueprint, request, jsonify
# from app import db
from extensions import db
from models.user import User
from models.checkin import Checkin

checkin_bp = Blueprint('checkin', __name__)

# 設計 POST /api/checkin API
@checkin_bp.route('/checkin', methods=['POST'])
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

    user = User.query.filter_by(line_user_id=line_user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    checkin = Checkin(user_id=user.user_id)
    db.session.add(checkin)
    db.session.commit()

    return jsonify({"message": "You have successfully checked in!"})

# 設計 GET /api/checkins/{user_id} API
@checkin_bp.route('/checkins/<int:user_id>', methods=['GET'])
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
        {"checkin_id": c.checkin_id, "checkin_time": c.checkin_time.isoformat()}
        for c in checkins
    ]
    return jsonify({"checkins": checkin_list})
