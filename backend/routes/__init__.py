"""
Routes module
Registers all blueprints
"""

from flask import Flask
from .auth_routes import auth_bp
from .health_routes import health_bp
from .ml_routes import ml_bp


def register_routes(app: Flask):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(ml_bp)

