"""
ML Routes
Handles ML model endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.ml_service import get_ml_service, get_vitamin_d_recommendations

logger = logging.getLogger(__name__)

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')


@ml_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict_health_risks():
    """Predict health risks using ML models"""
    current_user_email = get_jwt_identity()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    ml_service = get_ml_service()
    result = ml_service.predict_health_risks(data)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result), 200


@ml_bp.route('/vitamin-d/recommendations', methods=['POST'])
@jwt_required()
def get_vitamin_d_recs():
    """Get Vitamin D recommendations using trained ML model"""
    current_user_email = get_jwt_identity()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Call the get_vitamin_d_recommendations function
        result = get_vitamin_d_recommendations(data)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Error in Vitamin D recommendations: {str(e)}')
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/model-info', methods=['GET'])
@jwt_required()
def get_model_info():
    """Get information about ML models"""
    ml_service = get_ml_service()
    result = ml_service.get_model_info()
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result), 200


@ml_bp.route('/similar-patients', methods=['POST'])
@jwt_required()
def get_similar_patients():
    """Find similar patients and get recommendations"""
    current_user_email = get_jwt_identity()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    top_n = data.get('top_n', 5)
    
    ml_service = get_ml_service()
    result = ml_service.get_similar_patients(data, top_n)
    
    if 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result), 200


@ml_bp.route('/dynamic-recommendations', methods=['POST'])
@jwt_required()
def get_dynamic_recs():
    """Get dynamic recommendations with ML accuracy"""
    current_user_email = get_jwt_identity()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    ml_service = get_ml_service()
    result = ml_service.get_dynamic_recommendations(data)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result), 200


@ml_bp.route('/train', methods=['POST'])
@jwt_required()
def train_models():
    """Train ML models from dataset"""
    current_user_email = get_jwt_identity()
    
    data = request.get_json()
    if not data or 'file_path' not in data:
        return jsonify({'error': 'No file_path provided'}), 400
    
    file_path = data.get('file_path')
    model_types = data.get('model_types', ['random_forest'])
    
    ml_service = get_ml_service()
    result = ml_service.train_models(file_path, model_types)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result), 200
