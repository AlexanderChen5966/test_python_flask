from datetime import datetime
# from app import db
from extensions import db

class LineReply(db.Model):
    __tablename__ = 'line_reply'

    reply_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    reply_message = db.Column(db.Text, nullable=False)
    reply_time = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('line_replies', lazy=True))
