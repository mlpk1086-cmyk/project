"""
Health Routes
Handles health data and risk assessment endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

# Use absolute imports
from services.auth_service import AuthService
from services.health_service import get_health_service
from services.ai_service import get_ai_service
from services.recommendation_generator import generate_health_recommendations
from database import db, HealthData, RiskAssessment

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api')


@health_bp.route('/health-data', methods=['POST'])
@jwt_required()
def submit_health_data():
    """Submit health data endpoint"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Calculate BMI if height and weight provided
    height = float(data.get('height') or 0)
    weight = float(data.get('weight') or 0)
    bmi = 0
    
    if height > 0 and weight > 0:
        health_service = get_health_service()
        bmi = health_service.calculate_bmi(height, weight)
    
    # Create health data record
    health_data = HealthData(
        user_id=user.id,
        age=data.get('age'),
        height=height,
        weight=weight,
        bmi=bmi,
        gender=data.get('gender'),
        location=data.get('location'),
        systolic_bp=data.get('systolicBP'),
        diastolic_bp=data.get('diastolicBP'),
        heart_rate=data.get('heartRate'),
        total_cholesterol=data.get('totalCholesterol'),
        hdl_cholesterol=data.get('hdlCholesterol'),
        smoking_status=data.get('smokingStatus'),
        hemoglobin=data.get('hemoglobin'),
        vitamin_d=data.get('vitaminD'),
        fasting_blood_sugar=data.get('fastingBloodSugar'),
        physical_activity=data.get('physicalActivity', 'occasional')
    )
    
    try:
        db.session.add(health_data)
        db.session.commit()
        
        return jsonify({
            'message': 'Health data submitted successfully',
            'health_data': health_data.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error saving health data: {str(e)}')
        return jsonify({'error': f'Failed to save health data: {str(e)}'}), 500


@health_bp.route('/health-data', methods=['GET'])
@jwt_required()
def get_health_data():
    """Get health data endpoint"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get the most recent health data
    health_data = HealthData.query.filter_by(user_id=user.id).order_by(
        HealthData.created_at.desc()
    ).first()
    
    if not health_data:
        return jsonify({'error': 'No health data found'}), 404
    
    return jsonify(health_data.to_dict()), 200


@health_bp.route('/risks', methods=['GET'])
@jwt_required()
def calculate_risks():
    """Calculate health risks endpoint"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get the most recent health data
    health_data = HealthData.query.filter_by(user_id=user.id).order_by(
        HealthData.created_at.desc()
    ).first()
    
    if not health_data:
        return jsonify({'error': 'No health data found'}), 404
    
    # Calculate risks
    health_service = get_health_service()
    result = health_service.calculate_health_risks(health_data.to_dict())
    
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify({
        "risks": result["risks"], 
        "scores": result["scores"]
    }), 200


@health_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized recommendations endpoint"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get the most recent health data
    health_data_record = HealthData.query.filter_by(user_id=user.id).order_by(
        HealthData.created_at.desc()
    ).first()
    
    if not health_data_record:
        return jsonify({'error': 'No health data found'}), 404
    
    health_data = health_data_record.to_dict()
    
    # Calculate risks
    health_service = get_health_service()
    result = health_service.calculate_health_risks(health_data)
    
    if "error" in result:
        return jsonify(result), 500
    
    # Generate AI recommendations
    ai_service = get_ai_service()
    ai_recommendations = None
    
    if ai_service:
        ai_recommendations = ai_service.generate_recommendations(
            health_data, 
            result["risks"], 
            result["scores"]
        )
    
    # Generate parameter-based recommendations (dynamic based on individual values)
    param_based_result = health_service.generate_parameter_based_recommendations(health_data)
    
    response_data = {
        "health_data": health_data,
        "risks": result["risks"],
        "recommendations": result["recommendations"],
        "detailed_recommendations": result["detailed_recommendations"],
        "scores": result["scores"],
        "comprehensive_recommendations": result.get("comprehensive_recommendations", {}),
        "general_diet": result.get("general_diet", {}),
        "general_lifestyle": result.get("general_lifestyle", {}),
        "parameter_recommendations": param_based_result.get("parameter_recommendations", []),
        "parameters_triggered": param_based_result.get("parameters_triggered", {})
    }
    
    if ai_recommendations:
        response_data["ai_recommendations"] = ai_recommendations
    
    return jsonify(response_data), 200


@health_bp.route('/health-report', methods=['GET'])
@jwt_required()
def get_health_report():
    """Get complete health report endpoint"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get the most recent health data
    health_data_record = HealthData.query.filter_by(user_id=user.id).order_by(
        HealthData.created_at.desc()
    ).first()
    
    if not health_data_record:
        return jsonify({'error': 'No health data found'}), 404
    
    health_data = health_data_record.to_dict()
    
    # Calculate risks
    health_service = get_health_service()
    result = health_service.calculate_health_risks(health_data)
    
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify({
        'health_data': health_data,
        'risks': result["risks"],
        'scores': result["scores"],
        'recommendations': result["recommendations"],
        'detailed_recommendations': result["detailed_recommendations"]
    }), 200


@health_bp.route('/health-history', methods=['GET'])
@jwt_required()
def get_health_history():
    """Get health data history"""
    current_user_email = get_jwt_identity()
    
    user = AuthService.get_user_by_email(current_user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    health_records = HealthData.query.filter_by(user_id=user.id).order_by(
        HealthData.created_at.desc()
    ).limit(10).all()
    
    if not health_records:
        return jsonify({'error': 'No health data found'}), 404
    
    return jsonify({
        'history': [record.to_dict() for record in health_records]
    }), 200


@health_bp.route('/conditions', methods=['GET'])
@jwt_required()
def get_conditions():
    """Get all available conditions and their required data"""
    health_service = get_health_service()
    result = health_service.get_all_conditions_info()
    
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify(result), 200


@health_bp.route('/recommendations/diet/<disease>', methods=['GET'])
@jwt_required()
def get_diet_recs(disease):
    """Get diet recommendations for a specific disease"""
    risk_level = request.args.get('risk_level', 'low')
    
    health_service = get_health_service()
    result = health_service.get_diet_recommendations(disease, risk_level)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result), 200


@health_bp.route('/recommendations/lifestyle/<disease>', methods=['GET'])
@jwt_required()
def get_lifestyle_recs(disease):
    """Get lifestyle recommendations for a specific disease"""
    risk_level = request.args.get('risk_level', 'low')
    
    health_service = get_health_service()
    result = health_service.get_lifestyle_recommendations(disease, risk_level)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result), 200


@health_bp.route('/recommendations/actions/<disease>', methods=['GET'])
@jwt_required()
def get_actions(disease):
    """Get actionable steps for a specific disease"""
    risk_level = request.args.get('risk_level', 'low')
    
    health_service = get_health_service()
    result = health_service.get_actionable_steps(disease, risk_level)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result), 200


@health_bp.route('/recommendations/monitoring/<disease>', methods=['GET'])
@jwt_required()
def get_monitoring(disease):
    """Get monitoring schedule for a specific disease"""
    risk_level = request.args.get('risk_level', 'low')
    
    health_service = get_health_service()
    result = health_service.get_monitoring_schedule(disease, risk_level)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result), 200


@health_bp.route('/recommendations/comprehensive/<disease>', methods=['GET'])
@jwt_required()
def get_comprehensive(disease):
    """Get comprehensive recommendations for a specific disease"""
    risk_level = request.args.get('risk_level', 'low')
    
    health_service = get_health_service()
    result = health_service.get_comprehensive_recommendations(disease, risk_level)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result), 200


@health_bp.route('/required-data/<disease>', methods=['GET'])
@jwt_required()
def get_required_data(disease):
    """Get required health data fields for a specific disease"""
    health_service = get_health_service()
    result = health_service.get_required_health_data(disease)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result), 200


# New endpoint for JSON format recommendations
@health_bp.route('/analyze', methods=['POST'])
def analyze_health():
    """
    Analyze patient health data and generate recommendations in JSON format
    This endpoint doesn't require authentication for testing purposes
    Accepts patient data and returns structured recommendations
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        result = generate_health_recommendations(data)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f'Error generating recommendations: {str(e)}')
        return jsonify({'error': f'Failed to generate recommendations: {str(e)}'}), 500


@health_bp.route('/diabetes-predict', methods=['POST'])
def predict_diabetes_risk():
    """Diabetes-specific risk prediction using ML + rule-based scoring"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Rule-based from health service
        health_service = get_health_service()
        rule_result = health_service.calculate_health_risks(data)
        diabetes_rule = {
            'riskLevel': rule_result['risks']['diabetes'],
            'riskScore': rule_result['scores']['diabetes'],
            'recommendations': rule_result['detailed_recommendations']['diabetes']
        }
        
        # ML prediction if available
        ml_result = {}
        ml_service = get_ml_service()
        ml_pred = ml_service.predict_health_risks(data)
        if 'error' not in ml_pred:
            diabetes_ml = ml_pred['predictions'].get('diabetes_risk', {})
            ml_result = {
                'prediction': diabetes_ml.get('prediction', 'unknown'),
                'probabilities': diabetes_ml.get('probabilities', {}),
                'model_used': diabetes_ml.get('model_used', 'N/A')
            }
        
        return jsonify({
            'rule_based': diabetes_rule,
            'ml_based': ml_result,
            'full_data': data,
            'config_recs': rule_result.get('comprehensive_recommendations', {}).get('diabetes', {}),
            'parameter_recs': rule_result.get('parameter_recommendations', [])
        }), 200
        
    except Exception as e:
        logger.error(f'Error predicting diabetes risk: {str(e)}')
        return jsonify({'error': str(e)}), 500


