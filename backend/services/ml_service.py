"""
ML Service
Wrapper for ML model operations
"""

from typing import Dict, Any, Optional, List
import os
import logging

logger = logging.getLogger(__name__)


class MLService:
    """Service for ML model operations"""
    
    def __init__(self, models_dir: str = None, model_prefix: str = 'health_risk'):
        self.models_dir = models_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'models'
        )
        self.model_prefix = model_prefix
        self.predictor = None
        self.trainer = None
    
    def load_models(self) -> bool:
        """Load ML models"""
        try:
            from ml_models.predictor import HealthRiskPredictor
            
            self.predictor = HealthRiskPredictor(self.models_dir, self.model_prefix)
            return self.predictor.load_models()
        except Exception as e:
            logger.error(f'Error loading ML models: {str(e)}')
            return False
    
    def predict_health_risks(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict health risks using ML models
        
        Args:
            health_data: Dictionary containing health metrics
            
        Returns:
            Dictionary with predictions and recommendations
        """
        if self.predictor is None or not self.predictor.is_loaded:
            if not self.load_models():
                return {'error': 'ML models not available'}
        
        try:
            # Map input to expected format
            ml_input = {
                'age': health_data.get('age', 0),
                'bmi': health_data.get('bmi', 0),
                'gender': health_data.get('gender', 'unknown'),
                'systolicbp': health_data.get('systolicBP', 0),
                'diastolicbp': health_data.get('diastolicBP', 0),
                'heartrate': health_data.get('heartRate', 0),
                'totalcholesterol': health_data.get('totalCholesterol', 0),
                'hdlcholesterol': health_data.get('hdlCholesterol', 0),
                'hemoglobin': health_data.get('hemoglobin', 0),
                'vitamind': health_data.get('vitaminD', 0),
                'fastingbloodsugar': health_data.get('fastingBloodSugar', 0),
                'smokingstatus': health_data.get('smokingStatus', 'no'),
                'physicalactivity': health_data.get('physicalActivity', 'occasional'),
                'location': health_data.get('location', ''),
                'alcoholconsumption': health_data.get('alcoholConsumption', 'none'),
                'exerciselevel': health_data.get('exerciseLevel', 'occasional'),
                'ironpercentrda': health_data.get('ironPercentRda', 0),
                'familyhistorydiabetes': 1 if health_data.get('familyHistoryDiabetes', '').lower() == 'yes' else 0
            }

            
            predictions = self.predictor.predict_all_risks(ml_input)
            recommendations = self.predictor.get_ml_recommendations(predictions)
            
            return {
                'predictions': predictions,
                'recommendations': recommendations,
                'model_info': self.predictor.get_model_info()
            }
        except Exception as e:
            logger.error(f'Error predicting health risks: {str(e)}')
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about ML models"""
        if self.predictor is None:
            if not self.load_models():
                return {'error': 'ML models not available'}
        
        return self.predictor.get_model_info()
    
    def get_similar_patients(self, health_data: Dict[str, Any], 
                              top_n: int = 5) -> Dict[str, Any]:
        """Find similar patients and get recommendations"""
        try:
            from ml_models.predictor import get_similar_patients_recommendations
            
            ml_input = {
                'age': health_data.get('age', 0),
                'bmi': health_data.get('bmi', 0),
                'gender': health_data.get('gender', 'unknown'),
                'systolicbp': health_data.get('systolicBP', 0),
                'diastolicbp': health_data.get('diastolicBP', 0),
                'totalcholesterol': health_data.get('totalCholesterol', 0),
                'hdlcholesterol': health_data.get('hdlCholesterol', 0),
                'hemoglobin': health_data.get('hemoglobin', 0),
                'fastingbloodsugar': health_data.get('fastingBloodSugar', 0),
                'smokingstatus': health_data.get('smokingStatus', 'no')
            }
            
            xlsx_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'ml_models',
                'Healthcare_Risk_500_Patients_Final.xlsx'
            )
            
            if not os.path.exists(xlsx_path):
                return {'error': 'Patient dataset not found'}
            
            result = get_similar_patients_recommendations(ml_input, xlsx_path, top_n)
            return result
            
        except Exception as e:
            logger.error(f'Error getting similar patients: {str(e)}')
            return {'error': str(e)}
    
    def get_dynamic_recommendations(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get dynamic recommendations with ML accuracy"""
        try:
            from ml_models.predictor import get_dynamic_recommendations_with_accuracy
            
            ml_input = {
                'age': health_data.get('age', 0),
                'bmi': health_data.get('bmi', 0),
                'gender': health_data.get('gender', 'unknown'),
                'systolicbp': health_data.get('systolicBP', 0),
                'diastolicbp': health_data.get('diastolicBP', 0),
                'totalcholesterol': health_data.get('totalCholesterol', 0),
                'hdlcholesterol': health_data.get('hdlCholesterol', 0),
                'hemoglobin': health_data.get('hemoglobin', 0),
                'fastingbloodsugar': health_data.get('fastingBloodSugar', 0),
                'smokingstatus': health_data.get('smokingStatus', 'no')
            }
            
            xlsx_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'ml_models',
                'Healthcare_Risk_500_Patients_Final.xlsx'
            )
            
            if not os.path.exists(xlsx_path):
                return {'error': 'Patient dataset not found'}
            
            result = get_dynamic_recommendations_with_accuracy(ml_input, xlsx_path, self.models_dir)
            return result
            
        except Exception as e:
            logger.error(f'Error getting dynamic recommendations: {str(e)}')
            return {'error': str(e)}
    
    def train_models(self, file_path: str, model_types: List[str] = None) -> Dict[str, Any]:
        """Train ML models from dataset"""
        try:
            from ml_models.trainer import train_models_from_file
            
            if model_types is None:
                model_types = ['random_forest']
            
            result = train_models_from_file(file_path, self.models_dir, model_types)
            
            # Reload models after training
            self.load_models()
            
            return result
        except Exception as e:
            logger.error(f'Error training models: {str(e)}')
            return {'error': str(e)}


# Singleton instance
_ml_service = None


def get_ml_service(models_dir: str = None, model_prefix: str = 'health_risk') -> MLService:
    """Get or create ML service instance"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService(models_dir, model_prefix)
    return _ml_service


def get_vitamin_d_recommendations(health_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get Vitamin D recommendations using the trained ML model
    
    Args:
        health_data: Dictionary containing health metrics
        
    Returns:
        Dictionary with risk prediction and recommendations
    """
    import joblib
    import json
    import numpy as np
    import pandas as pd
    
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    
    try:
        # Load model files
        model_path = os.path.join(models_dir, 'vitamin_d_risk_random_forest.joblib')
        scaler_path = os.path.join(models_dir, 'vitamin_d_scaler.joblib')
        encoders_path = os.path.join(models_dir, 'vitamin_d_label_encoders.joblib')
        features_path = os.path.join(models_dir, 'vitamin_d_features.json')
        metrics_path = os.path.join(models_dir, 'vitamin_d_metrics.json')
        
        if not os.path.exists(model_path):
            return {'error': 'Vitamin D model not found'}
        
        # Load model and preprocessors
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        label_encoders = joblib.load(encoders_path)
        
        with open(features_path, 'r') as f:
            feature_columns = json.load(f)
        
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        # Map input data to feature columns
        # Frontend field names to model feature names
        input_mapping = {
            'age': 'age',
            'gender': 'gender',
            'bmi': 'bmi',
            'smoking_status': 'smoking_status',
            'alcohol_consumption': 'alcohol_consumption',
            'exercise_level': 'exercise_level',
            'diet_type': 'diet_type',
            'sun_exposure': 'sun_exposure',
            'vitamin_d_percent_rda': 'vitamin_d_percent_rda',
            'calcium_percent_rda': 'calcium_percent_rda',
            'iron_percent_rda': 'iron_percent_rda',
            'hemoglobin_g_dl': 'hemoglobin_g_dl',
            'serum_vitamin_d_ng_ml': 'serum_vitamin_d_ng_ml'
        }
        
        # Create input DataFrame
        input_data = {}
        for model_key, frontend_key in input_mapping.items():
            value = health_data.get(frontend_key, 0)
            
            # Encode categorical values
            if model_key in label_encoders:
                le = label_encoders[model_key]
                if value in le.classes_:
                    value = le.transform([value])[0]
                else:
                    value = 0
            
            input_data[model_key] = value
        
        # Create DataFrame with correct column order
        df = pd.DataFrame([input_data])[feature_columns]
        
        # Scale features
        X = scaler.transform(df)
        
        # Predict
        prediction = model.predict(X)[0]
        
        # Get risk level
        target_encoder = label_encoders.get('vitamin_d_risk')
        if target_encoder:
            risk_level = target_encoder.inverse_transform([prediction])[0]
        else:
            risk_level = 'low'
        
        # Generate recommendations based on risk level
        recommendations = {
            'high': {
                'title': 'High Vitamin D Deficiency Risk',
                'risk_level': 'High',
                'actions': [
                    'Consult a healthcare provider immediately',
                    'Consider Vitamin D3 supplementation (4000-10000 IU daily)',
                    'Get more sunlight exposure (30 mins daily)',
                    'Eat Vitamin D rich foods (fatty fish, fortified dairy, eggs)'
                ],
                'diet': [
                    'Fatty fish (salmon, mackerel, sardines)',
                    'Fortified milk and cereals',
                    'Egg yolks',
                    'Mushrooms exposed to UV light',
                    'Cheese'
                ],
                'lifestyle': [
                    'Increase sun exposure to 30 minutes daily',
                    'Consider UV lamp therapy in winter',
                    'Take Vitamin D supplements as prescribed',
                    'Regular blood testing every 3 months'
                ]
            },
            'moderate': {
                'title': 'Moderate Vitamin D Insufficiency',
                'risk_level': 'Moderate',
                'actions': [
                    'Consider Vitamin D3 supplementation (1000-2000 IU daily)',
                    'Increase sun exposure (15-20 mins daily)',
                    'Add Vitamin D rich foods to diet',
                    'Re-test Vitamin D levels in 3 months'
                ],
                'diet': [
                    'Fatty fish',
                    'Fortified plant milks',
                    'Egg yolks',
                    'Mushrooms'
                ],
                'lifestyle': [
                    'Moderate sun exposure daily',
                    'Maintain healthy weight',
                    'Regular outdoor exercise'
                ]
            },
            'low': {
                'title': 'Normal Vitamin D Levels',
                'risk_level': 'Low',
                'actions': [
                    'Maintain current healthy lifestyle',
                    'Continue regular sun exposure',
                    'Annual Vitamin D testing'
                ],
                'diet': [
                    'Balanced diet with Vitamin D sources',
                    'Continue fortified foods'
                ],
                'lifestyle': [
                    'Regular moderate sun exposure',
                    'Maintain healthy weight',
                    'Active lifestyle'
                ]
            }
        }
        
        result = recommendations.get(risk_level, recommendations['low'])
        result['model_accuracy'] = metrics.get('random_forest', {}).get('accuracy', 0.82)
        result['model_f1_score'] = metrics.get('random_forest', {}).get('f1', 0.82)
        
        return result
        
    except Exception as e:
        logger.error(f'Error getting Vitamin D recommendations: {str(e)}')
        return {'error': str(e)}

