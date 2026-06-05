"""
Database models for Healthcare Backend
SQLAlchemy models for User and HealthData
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with HealthData
    health_data = db.relationship('HealthData', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class HealthData(db.Model):
    """Health data model for storing patient health information"""
    __tablename__ = 'health_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Demographics
    age = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Float, nullable=True)  # cm
    weight = db.Column(db.Float, nullable=True)  # kg
    bmi = db.Column(db.Float, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    
    # Vital signs
    systolic_bp = db.Column(db.Integer, nullable=True)
    diastolic_bp = db.Column(db.Integer, nullable=True)
    heart_rate = db.Column(db.Integer, nullable=True)
    
    # Cholesterol
    total_cholesterol = db.Column(db.Float, nullable=True)
    hdl_cholesterol = db.Column(db.Float, nullable=True)
    
    # Blood tests
    hemoglobin = db.Column(db.Float, nullable=True)
    vitamin_d = db.Column(db.Float, nullable=True)
    fasting_blood_sugar = db.Column(db.Float, nullable=True)
    iron_percent_rda = db.Column(db.Float, nullable=True)
    
    # Lifestyle
    smoking_status = db.Column(db.String(20), nullable=True)
    physical_activity = db.Column(db.String(20), nullable=True, default='occasional')
    alcohol_consumption = db.Column(db.String(20), nullable=True)
    exercise_level = db.Column(db.String(20), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert health data to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.bmi,
            'gender': self.gender,
            'location': self.location,
            'systolicBP': self.systolic_bp,
            'diastolicBP': self.diastolic_bp,
            'heartRate': self.heart_rate,
            'totalCholesterol': self.total_cholesterol,
            'hdlCholesterol': self.hdl_cholesterol,
            'hemoglobin': self.hemoglobin,
            'vitaminD': self.vitamin_d,
            'fastingBloodSugar': self.fasting_blood_sugar,
            'ironPercentRda': self.iron_percent_rda,
            'smokingStatus': self.smoking_status,
            'physicalActivity': self.physical_activity,
            'alcoholConsumption': self.alcohol_consumption,
            'exerciseLevel': self.exercise_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict, user_id: int):
        """Create HealthData from dictionary"""
        return cls(
            user_id=user_id,
            age=data.get('age'),
            height=data.get('height'),
            weight=data.get('weight'),
            bmi=data.get('bmi'),
            gender=data.get('gender'),
            location=data.get('location'),
            systolic_bp=data.get('systolicBP'),
            diastolic_bp=data.get('diastolicBP'),
            heart_rate=data.get('heartRate'),
            total_cholesterol=data.get('totalCholesterol'),
            hdl_cholesterol=data.get('hdlCholesterol'),
            hemoglobin=data.get('hemoglobin'),
            vitamin_d=data.get('vitaminD'),
            fasting_blood_sugar=data.get('fastingBloodSugar'),
            iron_percent_rda=data.get('ironPercentRda'),
            smoking_status=data.get('smokingStatus'),
            physical_activity=data.get('physicalActivity', 'occasional'),
            alcohol_consumption=data.get('alcoholConsumption'),
            exercise_level=data.get('exerciseLevel')
        )
    
    def __repr__(self):
        return f'<HealthData user_id={self.user_id}>'


class RiskAssessment(db.Model):
    """Model for storing risk assessment results"""
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    health_data_id = db.Column(db.Integer, db.ForeignKey('health_data.id'), nullable=True)
    
    # Risk scores
    diabetes_score = db.Column(db.Integer, nullable=True)
    diabetes_risk = db.Column(db.String(20), nullable=True)
    
    anemia_score = db.Column(db.Integer, nullable=True)
    anemia_risk = db.Column(db.String(20), nullable=True)
    
    heart_score = db.Column(db.Integer, nullable=True)
    heart_risk = db.Column(db.String(20), nullable=True)
    
    vitamin_d_score = db.Column(db.Integer, nullable=True)
    vitamin_d_risk = db.Column(db.String(20), nullable=True)
    
    # AI recommendations
    ai_recommendations = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'health_data_id': self.health_data_id,
            'risks': {
                'diabetes': self.diabetes_risk,
                'anemia': self.anemia_risk,
                'heart': self.heart_risk,
                'vitamind': self.vitamin_d_risk
            },
            'scores': {
                'diabetes': self.diabetes_score,
                'anemia': self.anemia_score,
                'heart': self.heart_score,
                'vitamind': self.vitamin_d_score
            },
            'ai_recommendations': self.ai_recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<RiskAssessment user_id={self.user_id}>'

