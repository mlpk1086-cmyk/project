"""
Base Exception Classes
Custom exceptions for Healthcare API
"""

from typing import Any, Dict, Optional


class HealthcareException(Exception):
    """Base exception for all Healthcare API errors"""
    
    def __init__(
        self, 
        message: str = "An error occurred", 
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        result = {
            "error": self.__class__.__name__.replace('Exception', ''),
            "message": self.message
        }
        if self.details:
            result["details"] = self.details
        return result


class ValidationException(HealthcareException):
    """Exception raised for validation errors"""
    
    def __init__(
        self, 
        message: str = "Validation failed", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 400, details)


class AuthenticationException(HealthcareException):
    """Exception raised for authentication errors"""
    
    def __init__(
        self, 
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 401, details)


class AuthorizationException(HealthcareException):
    """Exception raised for authorization errors"""
    
    def __init__(
        self, 
        message: str = "Unauthorized access",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 403, details)


class ResourceNotFoundException(HealthcareException):
    """Exception raised when a resource is not found"""
    
    def __init__(
        self, 
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 404, details)


class ConflictException(HealthcareException):
    """Exception raised for resource conflicts"""
    
    def __init__(
        self, 
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 409, details)


class RateLimitException(HealthcareException):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 429, details)


class ExternalServiceException(HealthcareException):
    """Exception raised when external service fails"""
    
    def __init__(
        self, 
        message: str = "External service error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 502, details)


class DatabaseException(HealthcareException):
    """Exception raised for database errors"""
    
    def __init__(
        self, 
        message: str = "Database error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 500, details)


class MLServiceException(HealthcareException):
    """Exception raised for ML service errors"""
    
    def __init__(
        self, 
        message: str = "ML service error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 500, details)

