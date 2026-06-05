"""
Configuration module for Healthcare Backend
Manages environment variables and application settings
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up to backend folder from config folder
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)


class Config:
    """Application configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'healthcare-secret-key-2024')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    TESTING = False
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'healthcare-jwt-secret-2024')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours
    
    # Database settings - Point to config folder where database is located
    DATABASE_URI = os.getenv('DATABASE_URI', f'sqlite:///{BASE_DIR}/config/healthcare.db')
    
    # Upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # ML Model settings
    MODELS_DIR = os.getenv('MODELS_DIR', str(BASE_DIR / 'models'))
    MODEL_PREFIX = os.getenv('MODEL_PREFIX', 'health_risk')
    
    # AI/ML Service settings
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', '')
    AI_MODEL = os.getenv('AI_MODEL', 'gemini-2.0-flash')
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.7'))
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '2048'))
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'app.log'))
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration"""
        app.config['SECRET_KEY'] = cls.SECRET_KEY
        app.config['JWT_SECRET_KEY'] = cls.JWT_SECRET_KEY
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH
        
        # Ensure directories exist
        os.makedirs(cls.MODELS_DIR, exist_ok=True)
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary for different environments
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: Optional[str] = None) -> Config:
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)

