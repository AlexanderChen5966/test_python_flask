from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from extensions import db
from models.user import User
from models.checkin import Checkin

api = Namespace('Checkin', path='/api')

checkin_model = api.model('Checkin', {
    'line_user_id': fields.String(required=True, description='LINE user ID')
})


# 設計 POST /api/checkin API
@api.route('/checkin')
class CheckinResource(Resource):
    @api.expect(checkin_model)
    def post(self):
        data = request.get_json()
        line_user_id = data.get('line_user_id')
        user = User.query.filter_by(line_user_id=line_user_id).first()
        if not user:
            return {"message": "User not found"}, 404

        checkin = Checkin(user_id=user.user_id)
        db.session.add(checkin)
        db.session.commit()
        return {"message": "You have successfully checked in!"}

# 設計 GET /api/checkins/{user_id} API
class CheckinList(Resource):
    def get(self, user_id):
        checkins = Checkin.query.filter_by(user_id=user_id).all()
        checkin_list = [
            {"checkin_id": c.checkin_id, "checkin_time": c.checkin_time.isoformat()}
            for c in checkins
        ]
        return {"checkins": checkin_list}
