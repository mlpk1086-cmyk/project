"""
Database module
"""

from pathlib import Path
from flask import Flask
from .models import db, User, HealthData, RiskAssessment

# Get the backend directory path
BASE_DIR = Path(__file__).resolve().parent  # backend folder


def init_db(app: Flask):
    """Initialize database with Flask app"""
    # Get DATABASE_URI from app config
    database_uri = app.config.get('DATABASE_URI')
    
    if not database_uri:
        # Use default SQLite database in backend folder
        db_path = str(BASE_DIR / 'healthcare.db')
        database_uri = f'sqlite:///{db_path}'
        app.config['DATABASE_URI'] = database_uri
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = app.config.get('DEBUG', False)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return db


__all__ = ['db', 'User', 'HealthData', 'RiskAssessment', 'init_db']

