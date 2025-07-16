from datetime import datetime
# from app import db
from extensions import db

class Checkin(db.Model):
    __tablename__ = 'checkin'

    checkin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    checkin_time = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('checkins', lazy=True))
