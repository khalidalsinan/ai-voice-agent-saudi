from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Business(db.Model):
    __tablename__ = 'businesses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # Business hours (stored as JSON)
    business_hours = db.Column(db.Text, default='{}')
    
    # AI Configuration (stored as JSON)
    ai_config = db.Column(db.Text, default='{}')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    services = db.relationship('Service', backref='business', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='business', lazy=True, cascade='all, delete-orphan')
    call_logs = db.relationship('CallLog', backref='business', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'description': self.description,
            'business_hours': json.loads(self.business_hours) if self.business_hours else {},
            'ai_config': json.loads(self.ai_config) if self.ai_config else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    duration_minutes = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'business_id': self.business_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration_minutes': self.duration_minutes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    preferred_language = db.Column(db.String(10), default='ar')
    
    # Customer preferences (stored as JSON)
    preferences = db.Column(db.Text, default='{}')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='customer', lazy=True)
    call_logs = db.relationship('CallLog', backref='customer', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'preferred_language': self.preferred_language,
            'preferences': json.loads(self.preferences) if self.preferences else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    
    # Appointment details
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, completed, cancelled
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = db.relationship('Service', backref='appointments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'business_id': self.business_id,
            'customer_id': self.customer_id,
            'service_id': self.service_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'service': self.service.to_dict() if self.service else None,
            'customer': self.customer.to_dict() if self.customer else None
        }

class CallLog(db.Model):
    __tablename__ = 'call_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    
    # Call details
    call_sid = db.Column(db.String(100), unique=True)
    from_number = db.Column(db.String(20))
    to_number = db.Column(db.String(20))
    direction = db.Column(db.String(10))  # inbound, outbound
    status = db.Column(db.String(20))  # queued, ringing, in-progress, completed, failed
    duration = db.Column(db.Integer)  # in seconds
    
    # AI Processing results
    transcript = db.Column(db.Text)
    intent_detected = db.Column(db.String(50))
    outcome = db.Column(db.String(50))  # appointment_booked, info_provided, transferred, etc.
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'business_id': self.business_id,
            'customer_id': self.customer_id,
            'call_sid': self.call_sid,
            'from_number': self.from_number,
            'to_number': self.to_number,
            'direction': self.direction,
            'status': self.status,
            'duration': self.duration,
            'transcript': self.transcript,
            'intent_detected': self.intent_detected,
            'outcome': self.outcome,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'customer': self.customer.to_dict() if self.customer else None
        }

