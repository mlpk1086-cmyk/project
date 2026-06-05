"""
Security Headers Middleware
Adds security headers to responses
"""

from typing import Optional
from flask import Flask, Response, request
from functools import wraps


class SecurityHeadersMiddleware:
    """Middleware for adding security headers to responses"""
    
    def __init__(
        self,
        app: Optional[Flask] = None,
        cors_origins: str = '*',
        allowed_methods: Optional[list] = None,
        allowed_headers: Optional[list] = None
    ):
        """
        Initialize security middleware
        
        Args:
            app: Flask application
            cors_origins: CORS allowed origins (comma-separated)
            allowed_methods: Allowed HTTP methods
            allowed_headers: Allowed HTTP headers
        """
        self.app = app
        self.cors_origins = cors_origins.split(',')
        self.allowed_methods = allowed_methods or [
            'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'
        ]
        self.allowed_headers = allowed_headers or [
            'Content-Type', 'Authorization', 'X-Requested-With',
            'X-Request-ID', 'Accept', 'Accept-Language'
        ]
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app"""
        app.after_request(self.add_security_headers)
        app.after_request(self.add_cors_headers)
    
    def add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent XSS attacks
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Prevent content type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (basic)
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        # Strict Transport Security (if using HTTPS)
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    def add_cors_headers(self, response: Response) -> Response:
        """Add CORS headers to response"""
        # Get origin from request
        origin = request.headers.get('Origin', '')
        
        # Check if origin is allowed
        if '*' in self.cors_origins or origin in self.cors_origins:
            allowed_origin = '*' if '*' in self.cors_origins else origin
            
            response.headers['Access-Control-Allow-Origin'] = allowed_origin
            response.headers['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
            response.headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
        
        return response


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authentication is handled by JWT middleware
        # This is a placeholder for additional checks
        return f(*args, **kwargs)
    return decorated_function


def require_role(*roles):
    """
    Decorator to require specific roles
    
    Args:
        *roles: Allowed roles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Role checking is handled by JWT claims
            # This is a placeholder for additional checks
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_string: Raw input string
        
    Returns:
        Sanitized string
    """
    if not input_string:
        return ''
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$']
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Trim whitespace
    return sanitized.strip()


def validate_content_type(content_type: str) -> bool:
    """
    Validate content type for API requests
    
    Args:
        content_type: Content-Type header value
        
    Returns:
        True if valid
    """
    valid_types = [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data'
    ]
    
    return any(valid in content_type.lower() for valid in valid_types)

