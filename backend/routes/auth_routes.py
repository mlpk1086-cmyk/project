"""
Authentication Routes
Handles user registration and login endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

# Use absolute imports - services is at same level as routes
from services.auth_service import AuthService
from database import db

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('fullName', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    user, error = AuthService.register_user(email, password, full_name)
    
    if error:
        status_code = 400 if 'exists' in error.lower() else 500
        return jsonify({'error': error}), status_code
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user, access_token, error = AuthService.authenticate_user(email, password)
    
    if error:
        status_code = 401 if 'invalid' in error.lower() else 500
        return jsonify({'error': error}), status_code
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('fullName')
    success, error = AuthService.update_user(user, name)
    
    if not success:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    old_password = data.get('oldPassword', '')
    new_password = data.get('newPassword', '')
    
    if not old_password or not new_password:
        return jsonify({'error': 'Old and new password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
    
    success, error = AuthService.change_password(user, old_password, new_password)
    
    if not success:
        status_code = 400 if 'incorrect' in error.lower() else 500
        return jsonify({'error': error}), status_code
    
    return jsonify({'message': 'Password changed successfully'}), 200

