"""
Health Service
Handles health risk calculations and recommendations
"""

from typing import Dict, List, Optional, Any
import json
import os
import logging

logger = logging.getLogger(__name__)


class HealthService:
    """Service for health risk calculations"""
    
    def __init__(self):
        self.recommendations_config = self._load_recommendations_config()
    
    def _load_recommendations_config(self) -> Optional[Dict]:
        """Load recommendations configuration from JSON file"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'recommendations_config.json'
        )
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f'Error loading recommendations config: {e}')
            return None
    
    def calculate_bmi(self, height_cm: float, weight_kg: float) -> float:
        """Calculate BMI from height and weight"""
        if height_cm <= 0 or weight_kg <= 0:
            return 0.0
        height_m = height_cm / 100
        return round(weight_kg / (height_m * height_m), 2)
    
    def calculate_health_risks(self, health_data: Dict) -> Dict[str, Any]:
        """
        Calculate health risks based on input data
        
        Args:
            health_data: Dictionary containing health metrics
            
        Returns:
            Dictionary containing risks, scores, and recommendations
        """
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        risks = {}
        detailed_recommendations = {}
        scores = {}
        
        # Extract data with safe type conversion
        age = int(health_data.get('age') or 0)
        bmi = float(health_data.get('bmi') or 0)
        fbs = float(health_data.get('fastingBloodSugar') or health_data.get('BloodSugar') or 0)
        hb = float(health_data.get('hemoglobinGdl') or health_data.get('hemoglobin') or 0)
        # Handle Vitamin D - can come as serumVitaminDNgml, vitaminD, or vitaminDPercentRda
        vit_d = float(health_data.get('serumVitaminDNgml') or health_data.get('vitaminD') or 0)
        sys_bp = int(health_data.get('systolicBP') or 0)
        dia_bp = int(health_data.get('diastolicBP') or 0)
        total_chol = float(health_data.get('totalCholesterol') or 0)
        hdl_chol = float(health_data.get('hdlCholesterol') or 0)
        smoking = str(health_data.get('smokingStatus') or 'no').lower()
        gender = str(health_data.get('gender') or '').lower()
        location = str(health_data.get('location') or '').lower()
        physical_activity = str(health_data.get('physicalActivity') or health_data.get('exerciseLevel') or 'occasional').lower()
        family_history_diabetes = str(health_data.get('familyHistoryDiabetes') or health_data.get('familyHistory') or 'no').lower()
        
        conditions = self.recommendations_config.get('conditions', {})
        
        # Calculate Diabetes Risk (with new params)
        diabetes_score, diabetes_risk, diabetes_recs = self._calculate_diabetes_risk(
            bmi, fbs, age, physical_activity, family_history_diabetes, location, conditions
        )
        scores['diabetes'] = diabetes_score
        risks['diabetes'] = diabetes_risk
        detailed_recommendations['diabetes'] = diabetes_recs
        
        # Calculate Anemia Risk
        anemia_score, anemia_risk, anemia_recs = self._calculate_anemia_risk(
            hb, gender, age, conditions
        )
        scores['anemia'] = anemia_score
        risks['anemia'] = anemia_risk
        detailed_recommendations['anemia'] = anemia_recs
        
        # Calculate Vitamin D Risk
        vit_d_score, vit_d_risk, vit_d_recs = self._calculate_vitamin_d_risk(
            vit_d, location, conditions
        )
        scores['vitamind'] = vit_d_score
        risks['vitamind'] = vit_d_risk
        detailed_recommendations['vitamind'] = vit_d_recs
        
        # Calculate Heart Risk
        heart_score, heart_risk, heart_recs = self._calculate_heart_risk(
            sys_bp, dia_bp, total_chol, hdl_chol, smoking, bmi, physical_activity, conditions
        )
        scores['heart'] = heart_score
        risks['heart'] = heart_risk
        detailed_recommendations['heart'] = heart_recs
        
        # Combine all recommendations
        recommendations = []
        for condition_recs in detailed_recommendations.values():
            recommendations.extend(condition_recs)
        
        # Add general recommendations
        general_recs = self.recommendations_config.get('generalRecommendations', [])
        recommendations.extend(general_recs)
        
        # Remove duplicates while preserving order
        unique_recommendations = self._remove_duplicates(recommendations)
        
        # Get comprehensive recommendations for each disease
        comprehensive_details = {}
        for disease in ['diabetes', 'anemia', 'vitamind', 'heart']:
            risk = risks.get(disease, 'Low')
            comprehensive_details[disease] = self.get_comprehensive_recommendations(disease, risk)
        
        # Parameter-based recommendations
        param_based_result = self.generate_parameter_based_recommendations(health_data)
        
        return {
            "risks": risks,
            "recommendations": unique_recommendations,
            "detailed_recommendations": detailed_recommendations,
            "scores": scores,
            "comprehensive_recommendations": comprehensive_details,
            "general_diet": self.recommendations_config.get('generalDietRecommendations', {}),
            "general_lifestyle": self.recommendations_config.get('generalLifestyleRecommendations', {}),
            "parameter_recommendations": param_based_result.get("parameter_recommendations", []),
            "parameters_triggered": param_based_result.get("parameters_triggered", {})
        }

    
    def _calculate_diabetes_risk(self, bmi: float, fbs: float, age: int, 
                                  physical_activity: str, family_history: str, location: str, conditions: Dict) -> tuple:
        """Calculate diabetes risk score"""
        diabetes_score = 0
        diabetes_config = conditions.get('diabetes', {}).get('scoring', {})
        
        # BMI scoring
        if bmi >= 35:
            diabetes_score += diabetes_config.get('bmi', {}).get('>= 35', 25)
        elif bmi >= 30:
            diabetes_score += diabetes_config.get('bmi', {}).get('30-34.9', 20)
        elif bmi >= 25:
            diabetes_score += diabetes_config.get('bmi', {}).get('25-29.9', 10)
        
        # Fasting blood sugar scoring
        if fbs >= 126:
            diabetes_score += diabetes_config.get('fastingBloodSugar', {}).get('>= 126', 40)
        elif fbs >= 100:
            diabetes_score += diabetes_config.get('fastingBloodSugar', {}).get('100-125', 25)
        
        # Age scoring
        if age > 60:
            diabetes_score += diabetes_config.get('age', {}).get('> 60', 15)
        elif age > 45:
            diabetes_score += diabetes_config.get('age', {}).get('45-60', 10)
        
        # Physical activity scoring
        if physical_activity == 'none':
            diabetes_score += diabetes_config.get('physicalActivity', {}).get('none', 15)
        elif physical_activity == 'occasional':
            diabetes_score += diabetes_config.get('physicalActivity', {}).get('occasional', 10)
        
        # Family history scoring
        if family_history.lower() == 'yes':
            diabetes_score += diabetes_config.get('familyHistory', {}).get('yes', 20)
        
        # Location-specific (India: adjust for diet/lifestyle patterns)
        if 'india' in location.lower():
            # Higher risk due to carb-heavy diet, lower physical activity in urban areas
            diabetes_score += 5  # Conservative adjustment
        
        return self._determine_risk_level(diabetes_score, 'diabetes', conditions)

    
    def _calculate_anemia_risk(self, hemoglobin: float, gender: str, age: int, 
                                conditions: Dict) -> tuple:
        """Calculate anemia risk score"""
        anemia_score = 0
        anemia_config = conditions.get('anemia', {}).get('scoring', {})
        
        normal_hb = 13 if gender == "male" else 12
        
        # Hemoglobin scoring
        if hemoglobin < 8:
            anemia_score += anemia_config.get('hemoglobin', {}).get('< 8', 50)
        elif hemoglobin < 11:
            anemia_score += anemia_config.get('hemoglobin', {}).get('8-10.9', 35)
        elif hemoglobin < normal_hb:
            anemia_score += anemia_config.get('hemoglobin', {}).get('11-11.9', 20)
        
        # Gender scoring
        if gender == "female":
            anemia_score += anemia_config.get('gender', {}).get('female', 10)
        
        # Age scoring
        if age > 65:
            anemia_score += anemia_config.get('age', {}).get('> 65', 15)
        elif age > 50:
            anemia_score += anemia_config.get('age', {}).get('> 50', 10)
        
        return self._determine_risk_level(anemia_score, 'anemia', conditions)
    
    def _calculate_vitamin_d_risk(self, vitamin_d: float, location: str, 
                                   conditions: Dict) -> tuple:
        """Calculate vitamin D risk score"""
        vitamin_score = 0
        vitamin_config = conditions.get('vitamind', {}).get('scoring', {})
        
        # Vitamin D level scoring
        if vitamin_d < 10:
            vitamin_score += vitamin_config.get('vitaminD', {}).get('< 10', 50)
        elif vitamin_d < 20:
            vitamin_score += vitamin_config.get('vitaminD', {}).get('10-19', 35)
        elif vitamin_d < 30:
            vitamin_score += vitamin_config.get('vitaminD', {}).get('20-29', 20)
        
        # Location scoring
        if 'north' in location or 'canada' in location or 'uk' in location or 'winter' in location:
            vitamin_score += vitamin_config.get('location', {}).get('northern', 20)
        elif 'south' in location or 'tropical' in location or 'beach' in location:
            vitamin_score += vitamin_config.get('location', {}).get('tropical', 0)
        else:
            vitamin_score += vitamin_config.get('location', {}).get('temperate', 10)
        
        return self._determine_risk_level(vitamin_score, 'vitamind', conditions)
    
    def _calculate_heart_risk(self, systolic_bp: int, diastolic_bp: int, 
                               total_chol: float, hdl_chol: float, smoking: str,
                               bmi: float, physical_activity: str, conditions: Dict) -> tuple:
        """Calculate heart disease risk score"""
        heart_score = 0
        heart_config = conditions.get('heart', {}).get('scoring', {})
        
        # Systolic BP scoring
        if systolic_bp >= 180:
            heart_score += heart_config.get('systolicBP', {}).get('>= 180', 40)
        elif systolic_bp >= 140:
            heart_score += heart_config.get('systolicBP', {}).get('140-179', 30)
        elif systolic_bp >= 130:
            heart_score += heart_config.get('systolicBP', {}).get('130-139', 20)
        elif systolic_bp >= 120:
            heart_score += heart_config.get('systolicBP', {}).get('120-129', 10)
        
        # Diastolic BP scoring
        if diastolic_bp >= 120:
            heart_score += heart_config.get('diastolicBP', {}).get('>= 120', 40)
        elif diastolic_bp >= 90:
            heart_score += heart_config.get('diastolicBP', {}).get('90-119', 25)
        elif diastolic_bp >= 80:
            heart_score += heart_config.get('diastolicBP', {}).get('80-89', 15)
        
        # Cholesterol scoring
        if total_chol >= 240:
            heart_score += heart_config.get('totalCholesterol', {}).get('>= 240', 25)
        elif total_chol >= 200:
            heart_score += heart_config.get('totalCholesterol', {}).get('200-239', 15)
        
        # HDL cholesterol scoring
        if hdl_chol < 40:
            heart_score += heart_config.get('hdlCholesterol', {}).get('< 40', 15)
        elif hdl_chol < 60:
            heart_score += heart_config.get('hdlCholesterol', {}).get('40-59', 5)
        
        # Smoking scoring
        if smoking == 'yes':
            heart_score += heart_config.get('smokingStatus', {}).get('yes', 25)
        
        # BMI scoring
        if bmi >= 35:
            heart_score += heart_config.get('bmi', {}).get('>= 35', 15)
        elif bmi >= 30:
            heart_score += heart_config.get('bmi', {}).get('30-34.9', 10)
        elif bmi >= 25:
            heart_score += heart_config.get('bmi', {}).get('25-29.9', 5)
        
        # Physical activity scoring
        if physical_activity == 'none':
            heart_score += heart_config.get('physicalActivity', {}).get('none', 15)
        elif physical_activity == 'occasional':
            heart_score += heart_config.get('physicalActivity', {}).get('occasional', 10)
        
        return self._determine_risk_level(heart_score, 'heart', conditions)
    
    def _determine_risk_level(self, score: int, condition: str, 
                              conditions: Dict) -> tuple:
        """Determine risk level and get recommendations"""
        if score >= 60:
            risk = 'High'
            recommendations = conditions.get(condition, {}).get('riskLevels', {}).get('high', {}).get('recommendations', [])
        elif score >= 30:
            risk = 'Moderate'
            recommendations = conditions.get(condition, {}).get('riskLevels', {}).get('moderate', {}).get('recommendations', [])
        else:
            risk = 'Low'
            recommendations = conditions.get(condition, {}).get('riskLevels', {}).get('low', {}).get('recommendations', [])
        
        return score, risk, recommendations
    
    def _remove_duplicates(self, items: List) -> List:
        """Remove duplicates from list while preserving order"""
        seen = set()
        unique_items = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
        return unique_items
    
    def get_diet_recommendations(self, disease: str, risk_level: str) -> Dict[str, Any]:
        """
        Get diet recommendations for a specific disease and risk level
        
        Args:
            disease: Disease name (diabetes, anemia, vitamind, heart)
            risk_level: Risk level (low, moderate, high)
            
        Returns:
            Dictionary containing diet recommendations
        """
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        disease_key = disease.lower()
        risk_key = risk_level.lower()
        
        conditions = self.recommendations_config.get('conditions', {})
        disease_config = conditions.get(disease_key, {})
        
        if not disease_config:
            return {"error": f"Disease '{disease}' not found in configuration"}
        
        diet_recs = disease_config.get('dietRecommendations', {})
        
        return {
            "disease": disease_key,
            "risk_level": risk_key,
            "foods_to_eat": diet_recs.get('foodsToEat', []),
            "foods_to_avoid": diet_recs.get('foodsToAvoid', []),
            "meal_tips": diet_recs.get('mealTips', [])
        }
    
    def get_lifestyle_recommendations(self, disease: str, risk_level: str) -> Dict[str, Any]:
        """
        Get lifestyle recommendations for a specific disease and risk level
        
        Args:
            disease: Disease name (diabetes, anemia, vitamind, heart)
            risk_level: Risk level (low, moderate, high)
            
        Returns:
            Dictionary containing lifestyle recommendations
        """
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        disease_key = disease.lower()
        risk_key = risk_level.lower()
        
        conditions = self.recommendations_config.get('conditions', {})
        disease_config = conditions.get(disease_key, {})
        
        if not disease_config:
            return {"error": f"Disease '{disease}' not found in configuration"}
        
        lifestyle_recs = disease_config.get('lifestyleRecommendations', {})
        
        return {
            "disease": disease_key,
            "risk_level": risk_key,
            "exercise": lifestyle_recs.get('exercise', []),
            "sleep": lifestyle_recs.get('sleep', []),
            "stress_management": lifestyle_recs.get('stress', []),
            "habits": lifestyle_recs.get('habits', [])
        }
    
    def get_actionable_steps(self, disease: str, risk_level: str) -> Dict[str, Any]:
        """
        Get actionable steps for a specific disease and risk level
        
        Args:
            disease: Disease name (diabetes, anemia, vitamind, heart)
            risk_level: Risk level (low, moderate, high)
            
        Returns:
            Dictionary containing actionable steps
        """
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        disease_key = disease.lower()
        risk_key = risk_level.lower()
        
        conditions = self.recommendations_config.get('conditions', {})
        disease_config = conditions.get(disease_key, {})
        
        if not disease_config:
            return {"error": f"Disease '{disease}' not found in configuration"}
        
        actions = disease_config.get('recommendedActions', {})
        
        return {
            "disease": disease_key,
            "risk_level": risk_key,
            "immediate_actions": actions.get('immediate', []),
            "short_term_actions": actions.get('shortTerm', []),
            "long_term_actions": actions.get('longTerm', []),
            "recommended_tests": actions.get('tests', [])
        }
    
    def get_required_health_data(self, disease: str) -> Dict[str, Any]:
        """
        Get required health data fields for a specific disease
        
        Args:
            disease: Disease name (diabetes, anemia, vitamind, heart)
            
        Returns:
            Dictionary containing required data fields
        """
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        disease_key = disease.lower()
        
        conditions = self.recommendations_config.get('conditions', {})
        disease_config = conditions.get(disease_key, {})
        
        if not disease_config:
            return {"error": f"Disease '{disease}' not found in configuration"}
        
        return {
            "disease": disease_key,
            "required_data": disease_config.get('requiredData', []),
            "description": disease_config.get('description', ''),
            "name": disease_config.get('name', '')
        }
    
    def get_monitoring_schedule(self, disease: str, risk_level: str) -> Dict[str, Any]:
        """
        Get monitoring schedule for a specific disease and risk level
        
        Args:
            disease: Disease name (diabetes, anemia, vitamind, heart)
            risk_level: Risk level (low, moderate, high)
            
        Returns:
            Dictionary containing monitoring schedule
        """
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        disease_key = disease.lower()
        risk_key = risk_level.lower()
        
        conditions = self.recommendations_config.get('conditions', {})
        disease_config = conditions.get(disease_key, {})
        
        if not disease_config:
            return {"error": f"Disease '{disease}' not found in configuration"}
        
        monitoring = disease_config.get('monitoringSchedule', {})
        
        return {
            "disease": disease_key,
            "risk_level": risk_key,
            "schedule": monitoring.get(risk_key, {})
        }
    
    def get_comprehensive_recommendations(self, disease: str, risk_level: str) -> Dict[str, Any]:
        """
        Get comprehensive recommendations including all aspects for a disease
        
        Args:
            disease: Disease name (diabetes, anemia, vitamind, heart)
            risk_level: Risk level (low, moderate, high)
            
        Returns:
            Dictionary containing all recommendation types
        """
        diet = self.get_diet_recommendations(disease, risk_level)
        lifestyle = self.get_lifestyle_recommendations(disease, risk_level)
        actions = self.get_actionable_steps(disease, risk_level)
        monitoring = self.get_monitoring_schedule(disease, risk_level)
        
        # Get basic recommendations from risk levels
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        disease_key = disease.lower()
        risk_key = risk_level.lower()
        conditions = self.recommendations_config.get('conditions', {})
        disease_config = conditions.get(disease_key, {})
        risk_levels = disease_config.get('riskLevels', {})
        basic_recs = risk_levels.get(risk_key, {}).get('recommendations', [])
        
        return {
            "disease": disease_key,
            "risk_level": risk_key,
            "basic_recommendations": basic_recs,
            "diet": diet if isinstance(diet, dict) and "error" not in diet else {},
            "lifestyle": lifestyle if isinstance(lifestyle, dict) and "error" not in lifestyle else {},
            "actions": actions if isinstance(actions, dict) and "error" not in actions else {},
            "monitoring": monitoring if isinstance(monitoring, dict) and "error" not in monitoring else {}
        }
    
    def get_all_conditions_info(self) -> Dict[str, Any]:
        """
        Get information about all available conditions and their required data
        
        Returns:
            Dictionary containing all conditions info
        """
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        conditions = self.recommendations_config.get('conditions', {})
        result = {}
        
        for disease_key, disease_config in conditions.items():
            result[disease_key] = {
                "name": disease_config.get('name', ''),
                "description": disease_config.get('description', ''),
                "required_data": disease_config.get('requiredData', []),
                "factors": disease_config.get('factors', [])
            }
        
        return {
            "conditions": result,
            "general_diet": self.recommendations_config.get('generalDietRecommendations', {}),
            "general_lifestyle": self.recommendations_config.get('generalLifestyleRecommendations', {}),
            "general_recommendations": self.recommendations_config.get('generalRecommendations', [])
        }
    
    def generate_parameter_based_recommendations(self, health_data: Dict) -> Dict[str, Any]:
        """
        Generate recommendations based on individual parameter values,
        not just the overall risk level.
        
        Args:
            health_data: Dictionary containing health metrics
            
        Returns:
            Dictionary containing parameter-specific recommendations
        """
        if not self.recommendations_config:
            return {"error": "Recommendations configuration not loaded"}
        
        param_recs = self.recommendations_config.get('parameterRecommendations', {})
        all_recommendations = []
        parameters_triggered = {}
        
        # Process each disease category
        for disease, params_config in param_recs.items():
            disease_recs = []
            params = params_config.get('parameters', {})
            
            if disease == 'vitamind':
                disease_recs = self._process_vitamin_d_params(health_data, params)
            elif disease == 'diabetes':
                disease_recs = self._process_diabetes_params(health_data, params)
            elif disease == 'anemia':
                disease_recs = self._process_anemia_params(health_data, params)
            elif disease == 'heart':
                disease_recs = self._process_heart_params(health_data, params)
            
            if disease_recs:
                parameters_triggered[disease] = disease_recs
                all_recommendations.extend(disease_recs)
        
        # Remove duplicates while preserving order
        unique_recommendations = self._remove_duplicates(all_recommendations)
        
        return {
            "parameter_recommendations": unique_recommendations,
            "parameters_triggered": parameters_triggered,
            "total_count": len(unique_recommendations)
        }
    
    def _process_anemia_params(self, health_data: Dict, params: Dict) -> List[str]:
        """Process Anemia specific parameters"""
        recommendations = []
        
        # Map field names from frontend to config
        hemoglobin = health_data.get('hemoglobinGdl') or health_data.get('hemoglobin')
        iron_intake = health_data.get('ironIntake')
        vitamin_b12 = health_data.get('vitaminB12Level')
        gender = health_data.get('gender')
        
        # Hemoglobin
        if hemoglobin:
            try:
                hb_value = float(hemoglobin)
                if hb_value < 8:
                    recommendations.extend(params.get('hemoglobin', {}).get('< 8', {}).get('recommendations', []))
                elif hb_value < 10:
                    recommendations.extend(params.get('hemoglobin', {}).get('8-10.9', {}).get('recommendations', []))
                elif hb_value < 12:
                    recommendations.extend(params.get('hemoglobin', {}).get('10-12', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Iron Intake
        if iron_intake:
            iron_lower = str(iron_intake).lower()
            if iron_lower == 'low':
                recommendations.extend(params.get('ironIntake', {}).get('low', {}).get('recommendations', []))
            elif iron_lower == 'moderate':
                recommendations.extend(params.get('ironIntake', {}).get('moderate', {}).get('recommendations', []))
        
        # Vitamin B12
        if vitamin_b12:
            try:
                b12_value = float(vitamin_b12)
                if b12_value < 200:
                    recommendations.extend(params.get('vitaminB12', {}).get('< 200', {}).get('recommendations', []))
                elif b12_value < 400:
                    recommendations.extend(params.get('vitaminB12', {}).get('200-400', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Gender-specific recommendations
        if gender and str(gender).lower() == 'female':
            recommendations.extend(params.get('gender', {}).get('female', {}).get('recommendations', []))
        
        return recommendations
    
    def _process_heart_params(self, health_data: Dict, params: Dict) -> List[str]:
        """Process Heart specific parameters"""
        recommendations = []
        
        # Map field names from frontend to config
        systolic_bp = health_data.get('systolicBP')
        diastolic_bp = health_data.get('diastolicBP')
        total_chol = health_data.get('totalCholesterol')
        hdl_chol = health_data.get('hdlCholesterol')
        smoking = health_data.get('smokingStatus')
        physical = health_data.get('physicalActivity')
        
        # Systolic BP
        if systolic_bp:
            try:
                sys_value = float(systolic_bp)
                if sys_value >= 180:
                    recommendations.extend(params.get('systolicBP', {}).get('>= 180', {}).get('recommendations', []))
                elif sys_value >= 140:
                    recommendations.extend(params.get('systolicBP', {}).get('140-179', {}).get('recommendations', []))
                elif sys_value >= 130:
                    recommendations.extend(params.get('systolicBP', {}).get('130-139', {}).get('recommendations', []))
                elif sys_value >= 120:
                    recommendations.extend(params.get('systolicBP', {}).get('120-129', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Diastolic BP
        if diastolic_bp:
            try:
                dia_value = float(diastolic_bp)
                if dia_value >= 120:
                    recommendations.extend(params.get('diastolicBP', {}).get('>= 120', {}).get('recommendations', []))
                elif dia_value >= 90:
                    recommendations.extend(params.get('diastolicBP', {}).get('90-119', {}).get('recommendations', []))
                elif dia_value >= 80:
                    recommendations.extend(params.get('diastolicBP', {}).get('80-89', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Total Cholesterol
        if total_chol:
            try:
                chol_value = float(total_chol)
                if chol_value >= 240:
                    recommendations.extend(params.get('totalCholesterol', {}).get('>= 240', {}).get('recommendations', []))
                elif chol_value >= 200:
                    recommendations.extend(params.get('totalCholesterol', {}).get('200-239', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # HDL Cholesterol
        if hdl_chol:
            try:
                hdl_value = float(hdl_chol)
                if hdl_value < 40:
                    recommendations.extend(params.get('hdlCholesterol', {}).get('< 40', {}).get('recommendations', []))
                elif hdl_value < 60:
                    recommendations.extend(params.get('hdlCholesterol', {}).get('40-59', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Smoking Status
        if smoking:
            smoking_lower = str(smoking).lower()
            if smoking_lower == 'yes':
                recommendations.extend(params.get('smokingStatus', {}).get('yes', {}).get('recommendations', []))
        
        # Physical Activity
        if physical:
            physical_lower = str(physical).lower()
            if physical_lower == 'none' or physical_lower == 'sedentary':
                recommendations.extend(params.get('physicalActivity', {}).get('none', {}).get('recommendations', []))
            elif physical_lower == 'occasional':
                recommendations.extend(params.get('physicalActivity', {}).get('occasional', {}).get('recommendations', []))
        
        return recommendations
    
    def _process_vitamin_d_params(self, health_data: Dict, params: Dict) -> List[str]:
        """Process Vitamin D specific parameters"""
        recommendations = []
        
        # Map field names from frontend to config
        vitamin_d = health_data.get('serumVitaminDNgml') or health_data.get('vitaminD')
        sun_exposure = health_data.get('sunExposure')
        bmi = health_data.get('bmi')
        age = health_data.get('age')
        alcohol = health_data.get('alcoholConsumption')
        exercise = health_data.get('exerciseLevel')
        iron = health_data.get('ironPercentRda')
        hemoglobin = health_data.get('hemoglobin')
        
        # Serum Vitamin D
        if vitamin_d:
            try:
                vd_value = float(vitamin_d)
                if vd_value < 10:
                    recommendations.extend(params.get('serumVitaminD', {}).get('< 10', {}).get('recommendations', []))
                elif vd_value < 20:
                    recommendations.extend(params.get('serumVitaminD', {}).get('10-19', {}).get('recommendations', []))
                elif vd_value < 30:
                    recommendations.extend(params.get('serumVitaminD', {}).get('20-29', {}).get('recommendations', []))
                elif vd_value <= 100:
                    recommendations.extend(params.get('serumVitaminD', {}).get('30-100', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Sun Exposure (hours)
        if sun_exposure:
            try:
                se_value = float(sun_exposure)
                if se_value < 0.25:
                    recommendations.extend(params.get('sunExposure', {}).get('< 0.25', {}).get('recommendations', []))
                elif se_value < 0.5:
                    recommendations.extend(params.get('sunExposure', {}).get('0.25-0.5', {}).get('recommendations', []))
                elif se_value > 1:
                    recommendations.extend(params.get('sunExposure', {}).get('> 1', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # BMI
        if bmi:
            try:
                bmi_value = float(bmi)
                if bmi_value >= 35 or bmi_value >= 30:
                    recommendations.extend(params.get('bmi', {}).get('>= 30', {}).get('recommendations', []))
                elif bmi_value >= 25:
                    recommendations.extend(params.get('bmi', {}).get('25-29.9', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Age
        if age:
            try:
                age_value = int(age)
                if age_value > 65:
                    recommendations.extend(params.get('age', {}).get('> 65', {}).get('recommendations', []))
                elif age_value > 50:
                    recommendations.extend(params.get('age', {}).get('> 50', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Alcohol Consumption
        if alcohol:
            alcohol_lower = str(alcohol).lower()
            if alcohol_lower == 'heavy':
                recommendations.extend(params.get('alcoholConsumption', {}).get('heavy', {}).get('recommendations', []))
            elif alcohol_lower == 'moderate':
                recommendations.extend(params.get('alcoholConsumption', {}).get('moderate', {}).get('recommendations', []))
        
        # Exercise Level
        if exercise:
            exercise_lower = str(exercise).lower()
            if exercise_lower == 'none':
                recommendations.extend(params.get('exerciseLevel', {}).get('none', {}).get('recommendations', []))
        
        # Iron Percent RDA
        if iron:
            try:
                iron_value = float(iron)
                if iron_value < 50:
                    recommendations.extend(params.get('ironPercentRda', {}).get('< 50', {}).get('recommendations', []))
                elif iron_value < 75:
                    recommendations.extend(params.get('ironPercentRda', {}).get('50-75', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Hemoglobin
        if hemoglobin:
            try:
                hb_value = float(hemoglobin)
                if hb_value < 10:
                    recommendations.extend(params.get('hemoglobin', {}).get('< 10', {}).get('recommendations', []))
                elif hb_value < 12:
                    recommendations.extend(params.get('hemoglobin', {}).get('10-12', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        return recommendations
    
    def _process_diabetes_params(self, health_data: Dict, params: Dict) -> List[str]:
        """Process Diabetes specific parameters"""
        recommendations = []
        
        # Map field names from frontend to config
        fbs = health_data.get('fastingBloodSugar')
        hba1c = health_data.get('hbA1cLevel') or health_data.get('HbA1c')
        bmi = health_data.get('bmi')
        age = health_data.get('age')
        smoking = health_data.get('smokingStatus')
        physical = health_data.get('physicalActivity')
        sys_bp = health_data.get('systolicBP')
        total_chol = health_data.get('totalCholesterol')
        hdl = health_data.get('hdlCholesterol')
        
        # Fasting Blood Sugar
        if fbs:
            try:
                fbs_value = float(fbs)
                if fbs_value >= 126:
                    recommendations.extend(params.get('fastingBloodSugar', {}).get('>= 126', {}).get('recommendations', []))
                elif fbs_value >= 100:
                    recommendations.extend(params.get('fastingBloodSugar', {}).get('100-125', {}).get('recommendations', []))
                elif fbs_value >= 70:
                    recommendations.extend(params.get('fastingBloodSugar', {}).get('70-99', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # HbA1c
        if hba1c:
            try:
                hba1c_value = float(hba1c)
                if hba1c_value >= 6.5:
                    recommendations.extend(params.get('hbA1cLevel', {}).get('>= 6.5', {}).get('recommendations', []))
                elif hba1c_value >= 5.7:
                    recommendations.extend(params.get('hbA1cLevel', {}).get('5.7-6.4', {}).get('recommendations', []))
                elif hba1c_value < 5.7:
                    recommendations.extend(params.get('hbA1cLevel', {}).get('< 5.7', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # BMI
        if bmi:
            try:
                bmi_value = float(bmi)
                if bmi_value >= 35:
                    recommendations.extend(params.get('bmi', {}).get('>= 35', {}).get('recommendations', []))
                elif bmi_value >= 30:
                    recommendations.extend(params.get('bmi', {}).get('30-34.9', {}).get('recommendations', []))
                elif bmi_value >= 25:
                    recommendations.extend(params.get('bmi', {}).get('25-29.9', {}).get('recommendations', []))
                elif bmi_value >= 18.5:
                    recommendations.extend(params.get('bmi', {}).get('18.5-24.9', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Age
        if age:
            try:
                age_value = int(age)
                if age_value > 60:
                    recommendations.extend(params.get('age', {}).get('> 60', {}).get('recommendations', []))
                elif age_value >= 45:
                    recommendations.extend(params.get('age', {}).get('45-60', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Smoking Status
        if smoking:
            smoking_lower = str(smoking).lower()
            if smoking_lower == 'yes':
                recommendations.extend(params.get('smokingStatus', {}).get('yes', {}).get('recommendations', []))
        
        # Physical Activity
        if physical:
            physical_lower = str(physical).lower()
            if physical_lower == 'sedentary':
                recommendations.extend(params.get('physicalActivity', {}).get('sedentary', {}).get('recommendations', []))
            elif physical_lower == 'occasional':
                recommendations.extend(params.get('physicalActivity', {}).get('occasional', {}).get('recommendations', []))
            elif physical_lower in ['moderate', 'active']:
                recs = params.get('physicalActivity', {}).get('moderate', {}).get('recommendations', [])
                if recs:
                    recommendations.extend(recs)
                if physical_lower == 'active':
                    recs_active = params.get('physicalActivity', {}).get('active', {}).get('recommendations', [])
                    if recs_active:
                        recommendations.extend(recs_active)
        
        # Systolic BP
        if sys_bp:
            try:
                sys_value = float(sys_bp)
                if sys_value >= 140:
                    recommendations.extend(params.get('systolicBP', {}).get('>= 140', {}).get('recommendations', []))
                elif sys_value >= 130:
                    recommendations.extend(params.get('systolicBP', {}).get('130-139', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # Total Cholesterol
        if total_chol:
            try:
                chol_value = float(total_chol)
                if chol_value >= 240:
                    recommendations.extend(params.get('totalCholesterol', {}).get('>= 240', {}).get('recommendations', []))
                elif chol_value >= 200:
                    recommendations.extend(params.get('totalCholesterol', {}).get('200-239', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        # HDL Cholesterol
        if hdl:
            try:
                hdl_value = float(hdl)
                if hdl_value < 40:
                    recommendations.extend(params.get('hdlCholesterol', {}).get('< 40', {}).get('recommendations', []))
            except (ValueError, TypeError):
                pass
        
        return recommendations
    


# Singleton instance
_health_service = None


def get_health_service() -> HealthService:
    """Get or create health service instance"""
    global _health_service
    if _health_service is None:
        _health_service = HealthService()
    return _health_service

