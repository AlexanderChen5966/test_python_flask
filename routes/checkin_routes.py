from flask import Blueprint, request, jsonify
# from app import db
from extensions import db
from models.user import User
from models.checkin import Checkin

checkin_bp = Blueprint('checkin', __name__)

@checkin_bp.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    line_user_id = data.get('line_user_id')

    user = User.query.filter_by(line_user_id=line_user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    checkin = Checkin(user_id=user.user_id)
    db.session.add(checkin)
    db.session.commit()

    return jsonify({"message": "You have successfully checked in!"})


@checkin_bp.route('/checkins/<int:user_id>', methods=['GET'])
def get_checkins(user_id):
    checkins = Checkin.query.filter_by(user_id=user_id).all()
    checkin_list = [
        {"checkin_id": c.checkin_id, "checkin_time": c.checkin_time.isoformat()}
        for c in checkins
    ]
    return jsonify({"checkins": checkin_list})
