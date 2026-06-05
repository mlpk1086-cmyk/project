"""
Services module
Exports all service classes
"""

from .auth_service import AuthService
from .health_service import HealthService, get_health_service
from .ai_service import AIService, get_ai_service
from .ml_service import MLService, get_ml_service
from .recommendation_generator import (
    RecommendationGenerator,
    get_recommendation_generator,
    generate_health_recommendations
)

__all__ = [
    'AuthService',
    'HealthService',
    'get_health_service',
    'AIService',
    'get_ai_service',
    'MLService',
    'get_ml_service',
    'RecommendationGenerator',
    'get_recommendation_generator',
    'generate_health_recommendations'
]

