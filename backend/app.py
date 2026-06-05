"""
Healthcare Recommendation System - Backend API
Flask-based REST API for health risk assessment and recommendations

Version: 2.1.0
- Added input validation with Pydantic
- Added custom exception handling
- Added request/response logging middleware
- Added rate limiting
- Added security headers
"""

import os
import sys

# Get the backend directory path
backend_dir = os.path.dirname(os.path.abspath(__file__))
# Add parent directory to path for proper package imports
parent_dir = os.path.dirname(backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Import configuration
from config import get_config, Config

# Import database
from database import db, init_db

# Import routes
from routes import register_routes

# Import middleware
from middleware import (
    setup_logging,
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware
)

# Import exceptions
from exceptions import (
    HealthcareException,
    ValidationException,
    AuthenticationException,
    ResourceNotFoundException,
    ConflictException,
    RateLimitException,
    ExternalServiceException
)


def create_app(config_name: str = None) -> Flask:
    """Application factory for creating Flask app"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    config.init_app(app)
    
    # Setup logging with structured format
    setup_logging(
        app,
        log_level=app.config.get('LOG_LEVEL', 'INFO'),
        log_file=app.config.get('LOG_FILE'),
        json_format=False  # Set to True for JSON logging
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Healthcare API application...")
    
    # Initialize CORS with security options
    cors_origins = app.config.get('CORS_ORIGINS', '*')
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins.split(',') if isinstance(cors_origins, str) else cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"],
            "supports_credentials": True
        }
    })
    
    # Initialize JWT
    jwt = JWTManager(app)
    app.config['JWT_SECRET_KEY'] = app.config.get('JWT_SECRET_KEY', 'healthcare-jwt-secret-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=86400)
    
    # Set DATABASE_URI
    if 'DATABASE_URI' not in app.config:
        app.config['DATABASE_URI'] = Config.DATABASE_URI
    
    # Initialize database
    init_db(app)
    
    # Initialize middleware
    RequestLoggingMiddleware(app)
    RateLimitMiddleware(app, default_limit=100, default_window=60)
    SecurityHeadersMiddleware(app, cors_origins=cors_origins)
    
    # Register routes
    register_routes(app)
    
    # Register custom exception handlers
    register_exception_handlers(app)
    
    # Status endpoint
    @app.route('/api/status', methods=['GET'])
    @app.route('/api/v1/status', methods=['GET'])
    def status():
        return jsonify({
            'status': 'running',
            'message': 'Healthcare API is running',
            'version': '2.1.0'
        }), 200
    
    # Health check endpoint (no auth required)
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    
    logger.info("Healthcare API application started successfully")
    
    return app


def register_exception_handlers(app: Flask):
    """Register custom exception handlers for the Flask app"""
    
    @app.errorhandler(HealthcareException)
    def handle_healthcare_exception(error: HealthcareException):
        """Handle custom HealthcareException"""
        logger = logging.getLogger(__name__)
        logger.warning(f"Healthcare exception: {error.message}")
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(ValidationException)
    def handle_validation_exception(error: ValidationException):
        """Handle validation errors"""
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(AuthenticationException)
    def handle_auth_exception(error: AuthenticationException):
        """Handle authentication errors"""
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(ResourceNotFoundException)
    def handle_not_found(error: ResourceNotFoundException):
        """Handle resource not found errors"""
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(ConflictException)
    def handle_conflict(error: ConflictException):
        """Handle resource conflict errors"""
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(RateLimitException)
    def handle_rate_limit(error: RateLimitException):
        """Handle rate limit errors"""
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(ExternalServiceException)
    def handle_external_service(error: ExternalServiceException):
        """Handle external service errors"""
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'HTTP method not allowed'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger = logging.getLogger(__name__)
        logger.error(f"Internal server error: {str(error)}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(error)
        }), 500


# Create application instance
app = create_app()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("Healthcare Recommendation System - Backend API")
    print("=" * 60)
    print(f"Server running on http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print("API Endpoints:")
    print("  - POST /api/signup     : Register new user")
    print("  - POST /api/login      : User login")
    print("  - POST /api/health-data: Submit health data")
    print("  - GET  /api/risks      : Calculate health risks")
    print("  - GET  /api/recommendations: Get recommendations")
    print("  - GET  /api/health-report: Get health report")
    print("  - POST /api/ml/train   : Train ML models")
    print("  - POST /api/ml/predict: Predict with ML models")
    print("=" * 60)
    
    app.run(debug=debug, port=port, host='0.0.0.0')

