from datetime import datetime
from models import db

class Calculation(db.Model):
    __tablename__ = 'calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    expression = db.Column(db.String(500), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100), nullable=False)
    error_message = db.Column(db.String(200), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'expression': self.expression,
            'result': self.result,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f'<Calculation {self.id}: {self.expression} = {self.result}>'