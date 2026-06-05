"""
Healthcare Backend Exceptions
Custom exception classes for the Healthcare API
"""

from .base import (
    HealthcareException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    ConflictException,
    RateLimitException,
    ExternalServiceException
)

__all__ = [
    'HealthcareException',
    'ValidationException',
    'AuthenticationException',
    'AuthorizationException',
    'ResourceNotFoundException',
    'ConflictException',
    'RateLimitException',
    'ExternalServiceException'
]

