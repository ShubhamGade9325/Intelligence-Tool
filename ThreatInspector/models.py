from datetime import datetime
from app import db

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    indicator = db.Column(db.String(255), nullable=False)
    indicator_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.Column(db.JSON, nullable=True)  # Store API results as JSON
    
    def __repr__(self):
        return f"<SearchHistory {self.indicator}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'indicator': self.indicator,
            'indicator_type': self.indicator_type,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'results': self.results
        }

class ApiStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # "online", "offline", "error"
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f"<ApiStatus {self.service_name}: {self.status}>"
