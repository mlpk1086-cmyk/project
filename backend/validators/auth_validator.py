"""
Authentication Validators
Pydantic models for validating authentication-related requests
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


class SignUpValidator(BaseModel):
    """Validator for user registration"""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, max_length=100, description="User password")
    full_name: Optional[str] = Field(None, max_length=255, description="User full name")
    
    @validator('password')
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength"""
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean full name"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }
        }


class LoginValidator(BaseModel):
    """Validator for user login"""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class ProfileUpdateValidator(BaseModel):
    """Validator for profile update"""
    
    full_name: Optional[str] = Field(None, max_length=255, description="User full name")
    
    @validator('full_name')
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean full name"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe"
            }
        }


class PasswordChangeValidator(BaseModel):
    """Validator for password change"""
    
    old_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=6, max_length=100, description="New password")
    
    @validator('new_password')
    def validate_password_strength(cls, v: str) -> str:
        """Validate new password strength"""
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        return v
    
    @validator('old_password')
    def passwords_must_differ(cls, v: str, values: dict) -> str:
        """Ensure old and new passwords are different"""
        if 'new_password' in values and v == values['new_password']:
            raise ValueError('New password must be different from old password')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "OldSecurePass123",
                "new_password": "NewSecurePass456"
            }
        }


class TokenValidator(BaseModel):
    """Validator for token refresh"""
    
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

