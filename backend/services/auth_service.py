"""
Authentication Service
Handles user authentication and registration
"""

from typing import Optional, Tuple, Dict
from flask_jwt_extended import create_access_token
import logging

# Use absolute imports
from database import db, User

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations"""
    
    @staticmethod
    def register_user(email: str, password: str, full_name: str = '') -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user
        
        Args:
            email: User's email address
            password: User's password
            full_name: User's full name
            
        Returns:
            Tuple of (User or None, error message or None)
        """
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email.lower()).first()
            if existing_user:
                return None, 'User already exists'
            
            # Create new user
            user = User(
                email=email.lower(),
                name=full_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f'New user registered: {email}')
            return user, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error registering user: {str(e)}')
            return None, f'Registration failed: {str(e)}'
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Tuple[Optional[User], Optional[str], Optional[str]]:
        """
        Authenticate user and generate access token
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (User or None, access_token or None, error message or None)
        """
        try:
            user = User.query.filter_by(email=email.lower()).first()
            
            if not user:
                return None, None, 'Invalid credentials'
            
            if not user.check_password(password):
                return None, None, 'Invalid credentials'
            
            # Generate access token
            access_token = create_access_token(identity=user.email)
            
            logger.info(f'User logged in: {email}')
            return user, access_token, None
            
        except Exception as e:
            logger.error(f'Error authenticating user: {str(e)}')
            return None, None, f'Authentication failed: {str(e)}'
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address"""
        return User.query.filter_by(email=email.lower()).first()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def update_user(user: User, name: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Update user information
        
        Args:
            user: User object to update
            name: New name (optional)
            
        Returns:
            Tuple of (success, error message)
        """
        try:
            if name is not None:
                user.name = name
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating user: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Change user password
        
        Args:
            user: User object
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, error message)
        """
        try:
            if not user.check_password(old_password):
                return False, 'Current password is incorrect'
            
            user.set_password(new_password)
            db.session.commit()
            
            logger.info(f'Password changed for user: {user.email}')
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error changing password: {str(e)}')
            return False, str(e)

