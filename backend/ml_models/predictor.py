"""
ML Model Predictor for Healthcare Recommendation System
Handles predictions using trained ML models
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime

from .preprocessing import HealthcareDataPreprocessor, preprocess_health_data

class HealthRiskPredictor:
    """Predictor class for healthcare risk prediction"""
    
    def __init__(self, models_dir='models', prefix='health_risk'):
        self.models_dir = models_dir
        self.prefix = prefix
        self.preprocessor = None
        self.models = {}
        self.model_metrics = {}
        self.is_loaded = False
        
    def load_models(self):
        """Load trained models and preprocessor"""
        # Load preprocessor
        preprocessor_path = os.path.join(self.models_dir, f'{self.prefix}_preprocessor.joblib')
        if os.path.exists(preprocessor_path):
            self.preprocessor = HealthcareDataPreprocessor.load(preprocessor_path)
        
        # Load all available models
        model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.joblib') and f != f'{self.prefix}_preprocessor.joblib']
        
        for model_file in model_files:
            model_path = os.path.join(self.models_dir, model_file)
            model_key = model_file.replace(f'{self.prefix}_', '').replace('.joblib', '')
            self.models[model_key] = joblib.load(model_path)
        
        # Load metrics
        metrics_path = os.path.join(self.models_dir, f'{self.prefix}_metrics.json')
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                self.model_metrics = json.load(f)
        
        self.is_loaded = len(self.models) > 0
        return self.is_loaded
    
    def predict_single(self, health_data, target='diabetes_risk'):
        """Predict risk for a single health data record"""
        if not self.is_loaded:
            raise ValueError("Models not loaded. Call load_models() first.")
        
        # Map target to model key
        model_key = f"{target}_random_forest"
        
        if model_key not in self.models:
            # Try other model types
            for model_type in ['gradient_boosting', 'logistic_regression']:
                model_key = f"{target}_{model_type}"
                if model_key in self.models:
                    break
            else:
                raise ValueError(f"No model found for target: {target}")
        
        # Preprocess input data
        X = preprocess_health_data(health_data, self.preprocessor)
        
        # Make prediction
        model = self.models[model_key]
        prediction = model.predict(X)[0]
        
        # Get prediction probabilities if available
        probabilities = {}
        if hasattr(model, 'predict_proba'):
            probas = model.predict_proba(X)[0]
            classes = model.classes_
            probabilities = {str(cls): float(prob) for cls, prob in zip(classes, probas)}
        
        return {
            'target': target,
            'prediction': str(prediction),
            'probabilities': probabilities,
            'model_used': model_key
        }
    
    def predict_all_risks(self, health_data):
        """Predict all health risks for a single record"""
        if not self.is_loaded:
            raise ValueError("Models not loaded. Call load_models() first.")
        
        targets = ['diabetes_risk', 'anemia_risk', 'heart_risk', 'vitamind_risk']
        
        predictions = {}
        
        for target in targets:
            try:
                result = self.predict_single(health_data, target)
                predictions[target] = result
            except Exception as e:
                predictions[target] = {'error': str(e)}
        
        return predictions
    
    def get_model_info(self):
        """Get information about loaded models"""
        return {
            'is_loaded': self.is_loaded,
            'models_available': list(self.models.keys()),
            'metrics': self.model_metrics
        }
    
    def get_risk_level(self, score, thresholds=None):
        """Convert risk score to risk level"""
        if thresholds is None:
            thresholds = {
                'high': 0.7,
                'moderate': 0.4,
                'low': 0.0
            }
        
        if score >= thresholds['high']:
            return 'High'
        elif score >= thresholds['moderate']:
            return 'Moderate'
        else:
            return 'Low'
    
    def get_ml_recommendations(self, predictions):
        """Generate recommendations based on ML predictions"""
        recommendations = []
        
        risk_recommendations = {
            'diabetes_risk': {
                'high': [
                    'Consult with an endocrinologist immediately',
                    'Follow a strict low-carbohydrate diet under medical supervision',
                    'Begin regular blood glucose monitoring',
                    'Consider diabetes prevention program enrollment',
                    'Increase physical activity to 300 minutes per week'
                ],
                'moderate': [
                    'Reduce sugar and refined carbohydrate intake',
                    'Increase physical activity to at least 150 minutes per week',
                    'Monitor blood sugar levels every 6 months',
                    'Consult with a healthcare provider for personalized advice'
                ],
                'low': [
                    'Maintain a healthy lifestyle with regular physical activity',
                    'Continue monitoring blood sugar levels annually',
                    'Follow a balanced diet rich in fiber and whole grains'
                ]
            },
            'anemia_risk': {
                'high': [
                    'Seek immediate medical evaluation',
                    'Prescribed iron supplements may be required',
                    'Consider vitamin B12 and folate supplements',
                    'Address underlying causes (GI issues, heavy menstrual bleeding)',
                    'Schedule urgent appointment with hematologist'
                ],
                'moderate': [
                    'Increase intake of iron-rich foods (leafy greens, beans, red meat)',
                    'Consider iron supplements after consulting a doctor',
                    'Ensure adequate vitamin C intake',
                    'Schedule follow-up blood tests in 3 months'
                ],
                'low': [
                    'Maintain a balanced diet with iron-rich foods',
                    'Continue regular health check-ups',
                    'Include vitamin C in your diet for better iron absorption'
                ]
            },
            'heart_risk': {
                'high': [
                    'Consult cardiologist immediately',
                    'Follow strict DASH or Mediterranean diet',
                    'Begin structured exercise program under supervision',
                    'Quit smoking if currently smoking',
                    'Consider blood pressure medication',
                    'Monitor cholesterol levels with statin therapy if prescribed'
                ],
                'moderate': [
                    'Reduce sodium intake to less than 2300mg daily',
                    'Increase physical activity to 150 minutes per week',
                    'Follow DASH diet approach',
                    'Limit alcohol consumption',
                    'Monitor blood pressure regularly at home'
                ],
                'low': [
                    'Maintain heart-healthy lifestyle',
                    'Continue regular physical activity',
                    'Follow a balanced diet low in saturated fats',
                    'Monitor blood pressure annually'
                ]
            },
            'vitamind_risk': {
                'high': [
                    'Start high-dose vitamin D supplementation immediately',
                    'Consult with a healthcare provider for proper dosage',
                    'Test for underlying conditions causing deficiency',
                    'Increase sun exposure to 30-60 minutes daily if possible',
                    'Consider calcium supplementation for bone health'
                ],
                'moderate': [
                    'Increase sun exposure safely (15-30 minutes daily)',
                    'Consume more fatty fish, fortified dairy, and eggs',
                    'Consider vitamin D supplements (1000-2000 IU daily)',
                    'Re-test vitamin D levels in 3-6 months'
                ],
                'low': [
                    'Maintain current vitamin D levels through balanced diet',
                    'Continue regular sun exposure (10-15 minutes daily)',
                    'Include vitamin D-rich foods in diet'
                ]
            }
        }
        
        for target, pred in predictions.items():
            if 'error' in pred:
                continue
            
            prediction = pred.get('prediction', '')
            probabilities = pred.get('probabilities', {})
            
            # Get highest probability class
            if probabilities:
                max_prob_class = max(probabilities, key=probabilities.get)
                risk_level = self.get_risk_level(probabilities.get(max_prob_class, 0))
            else:
                risk_level = prediction if prediction in ['high', 'moderate', 'low'] else 'Low'
            
            # Add recommendations
            if target in risk_recommendations:
                recs = risk_recommendations[target].get(risk_level.lower(), [])
                recommendations.extend(recs)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recs.append(rec)
        
        return unique_recs


# Global predictor instance
_predictor = None

def get_predictor(models_dir='models', prefix='health_risk'):
    """Get or create global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = HealthRiskPredictor(models_dir, prefix)
        _predictor.load_models()
    return _predictor


def predict_health_risks(health_data, models_dir='models'):
    """Convenience function to predict health risks"""
    predictor = HealthRiskPredictor(models_dir)
    if not predictor.load_models():
        raise ValueError("No trained models found. Please train models first.")
    
    predictions = predictor.predict_all_risks(health_data)
    recommendations = predictor.get_ml_recommendations(predictions)
    
    return {
        'predictions': predictions,
        'recommendations': recommendations,
        'model_info': predictor.get_model_info()
    }


def get_similar_patients_recommendations(health_data, xlsx_path, top_n=5):
    """
    Find similar patients from the XLSX dataset and get their recommendations
    This provides personalized recommendations based on similar patient outcomes
    """
    from .preprocessing import load_xlsx_dataset
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    
    # Load the XLSX dataset
    df = load_xlsx_dataset(xlsx_path)
    
    # Features to use for similarity calculation
    feature_cols = ['age', 'bmi', 'systolicbp', 'diastolicbp', 
                    'totalcholesterol', 'hdlcholesterol', 'hemoglobin', 'fastingbloodsugar']
    
    # Check which columns are available
    available_features = [col for col in feature_cols if col in df.columns]
    
    if not available_features:
        return {'error': 'Required features not found in dataset'}
    
    # Prepare patient data
    patient_features = []
    for col in available_features:
        val = health_data.get(col, 0)
        if val is None:
            val = 0
        patient_features.append(float(val))
    
    # Get dataset features
    dataset_features = df[available_features].copy()
    
    # Normalize
    scaler = StandardScaler()
    dataset_normalized = scaler.fit_transform(dataset_features)
    patient_normalized = scaler.transform([patient_features])
    
    # Calculate distances to all patients
    distances = np.sqrt(np.sum((dataset_normalized - patient_normalized) ** 2, axis=1))
    
    # Get top N similar patients
    similar_indices = np.argsort(distances)[:top_n]
    similar_patients = df.iloc[similar_indices]
    
    # Collect recommendations from similar patients
    recommendations = {
        'diabetes': [],
        'anemia': [],
        'heart': [],
        'vitamind': []
    }
    
    risk_levels = {
        'diabetes': [],
        'anemia': [],
        'heart': [],
        'vitamind': []
    }
    
    # Default recommendations based on risk levels (used when no recommendation columns exist)
    default_recommendations = {
        'diabetes': {
            'high': ['Consult with an endocrinologist immediately', 'Follow a strict low-carbohydrate diet', 'Begin regular blood glucose monitoring'],
            'moderate': ['Reduce sugar intake', 'Increase physical activity', 'Monitor blood sugar every 6 months'],
            'low': ['Maintain healthy lifestyle', 'Continue annual monitoring']
        },
        'anemia': {
            'high': ['Seek immediate medical evaluation', 'Consider iron supplements', 'Schedule appointment with hematologist'],
            'moderate': ['Increase iron-rich foods', 'Consider iron supplements after consulting doctor', 'Ensure adequate vitamin C intake'],
            'low': ['Maintain balanced diet', 'Continue regular health check-ups']
        },
        'heart': {
            'high': ['Consult cardiologist immediately', 'Follow DASH diet', 'Begin supervised exercise program', 'Quit smoking'],
            'moderate': ['Reduce sodium intake', 'Increase physical activity', 'Follow DASH diet approach'],
            'low': ['Maintain heart-healthy lifestyle', 'Continue regular physical activity']
        },
        'vitamind': {
            'high': ['Start high-dose vitamin D supplementation', 'Consult healthcare provider', 'Increase sun exposure'],
            'moderate': ['Increase sun exposure safely', 'Consume fatty fish and fortified dairy', 'Consider supplements'],
            'low': ['Maintain current vitamin D levels', 'Continue regular sun exposure']
        }
    }

    for idx, row in similar_patients.iterrows():
        # Check for recommendation columns first
        has_recommendations = False
        if 'diabetes_recommendation' in row:
            rec = row.get('diabetes_recommendation', '')
            if pd.notna(rec) and rec:
                recommendations['diabetes'].append(rec)
                has_recommendations = True
        if 'anemia_recommendation' in row:
            rec = row.get('anemia_recommendation', '')
            if pd.notna(rec) and rec:
                recommendations['anemia'].append(rec)
                has_recommendations = True
        if 'heart_recommendation' in row:
            rec = row.get('heart_recommendation', '')
            if pd.notna(rec) and rec:
                recommendations['heart'].append(rec)
                has_recommendations = True
        if 'vitamind_recommendation' in row:
            rec = row.get('vitamind_recommendation', '')
            if pd.notna(rec) and rec:
                recommendations['vitamind'].append(rec)
                has_recommendations = True
        
        # Always collect risk levels
        if 'diabetes_risk' in row:
            risk_levels['diabetes'].append(row.get('diabetes_risk', ''))
        if 'anemia_risk' in row:
            risk_levels['anemia'].append(row.get('anemia_risk', ''))
        if 'heart_risk' in row:
            risk_levels['heart'].append(row.get('heart_risk', ''))
        if 'vitamind_risk' in row:
            risk_levels['vitamind'].append(row.get('vitamind_risk', ''))
        
        # If no recommendation columns found, add default recommendations based on risk levels
        if not has_recommendations:
            for condition in ['diabetes', 'anemia', 'heart', 'vitamind']:
                risk_col = condition + '_risk'
                if risk_col in row.columns or condition in risk_levels:
                    risk_val = row.get(risk_col, '')
                    if pd.notna(risk_val) and risk_val:
                        risk_key = str(risk_val).lower()
                        if risk_key in default_recommendations.get(condition, {}):
                            recommendations[condition].extend(default_recommendations[condition][risk_key])
    
    # Aggregate recommendations - get most common/important ones
    aggregated_recommendations = {}
    aggregated_risks = {}
    
    for condition in recommendations:
        # Get unique recommendations (remove duplicates)
        unique_recs = list(dict.fromkeys(recommendations[condition]))
        aggregated_recommendations[condition] = unique_recs
        
        # Get most common risk level
        risk_list = [r for r in risk_levels[condition] if r]
        if risk_list:
            # Count risk levels
            from collections import Counter
            risk_counts = Counter(risk_list)
            most_common_risk = risk_counts.most_common(1)[0][0]
            aggregated_risks[condition] = most_common_risk
    
    return {
        'similar_patients_count': top_n,
        'recommendations': aggregated_recommendations,
        'risk_levels': aggregated_risks,
        'similarity_scores': distances[similar_indices].tolist()
    }


def get_dynamic_recommendations_with_accuracy(health_data, xlsx_path, models_dir='models'):
    """
    Get dynamic recommendations based on:
    1. ML model predictions with accuracy metrics
    2. Similar patient recommendations from XLSX data
    """
    result = {
        'ml_predictions': None,
        'similar_patients': None,
        'combined_recommendations': {},
        'accuracy': {}
    }
    
    # Try ML predictions if models exist
    try:
        predictor = HealthRiskPredictor(models_dir)
        if predictor.load_models():
            predictions = predictor.predict_all_risks(health_data)
            ml_recommendations = predictor.get_ml_recommendations(predictions)
            
            result['ml_predictions'] = predictions
            result['ml_recommendations'] = ml_recommendations
            
            # Get accuracy from model metrics
            model_info = predictor.get_model_info()
            result['accuracy'] = model_info.get('metrics', {})
    except Exception as e:
        result['ml_error'] = str(e)
    
    # Get similar patient recommendations
    try:
        similar_result = get_similar_patients_recommendations(health_data, xlsx_path)
        result['similar_patients'] = similar_result
        
        if 'error' not in similar_result:
            # Combine recommendations
            for condition in ['diabetes', 'anemia', 'heart', 'vitamind']:
                combined = []
                
                # Add ML recommendations
                if 'ml_recommendations' in result:
                    combined.extend(result.get('ml_recommendations', []))
                
                # Add similar patient recommendations
                if condition in similar_result.get('recommendations', {}):
                    combined.extend(similar_result['recommendations'][condition])
                
                # Remove duplicates
                seen = set()
                unique_recs = []
                for rec in combined:
                    if rec not in seen:
                        seen.add(rec)
                        unique_recs.append(rec)
                
                result['combined_recommendations'][condition] = unique_recs
    except Exception as e:
        result['similar_error'] = str(e)
    
    return result
