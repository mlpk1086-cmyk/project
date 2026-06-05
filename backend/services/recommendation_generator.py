"""
Recommendation Generator Service
Generates medical risk analysis and personalized recommendations in JSON format
for React dashboard display
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class RecommendationGenerator:
    """Generate medical risk analysis and recommendations in specific JSON format"""
    
    def __init__(self):
        pass
    
    def analyze_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patient health data and generate recommendations
        
        Args:
            patient_data: Dictionary containing patient health parameters
            
        Returns:
            Dictionary with risk analysis and recommendations in JSON format
        """
        # Extract patient parameters with safe defaults
        age = int(patient_data.get('age') or 0)
        gender = str(patient_data.get('gender') or 'male').lower()
        height = float(patient_data.get('height') or 0)
        weight = float(patient_data.get('weight') or 0)
        bmi = float(patient_data.get('bmi') or 0)
        systolic_bp = int(patient_data.get('systolicBP') or patient_data.get('systolic_bp') or 0)
        diastolic_bp = int(patient_data.get('diastolicBP') or patient_data.get('diastolic_bp') or 0)
        total_cholesterol = float(patient_data.get('totalCholesterol') or 0)
        hdl_cholesterol = float(patient_data.get('hdlCholesterol') or 0)
        hemoglobin = float(patient_data.get('hemoglobin') or 0)
        smoking = str(patient_data.get('smoking') or patient_data.get('smokingStatus') or 'no').lower()
        blood_sugar = float(patient_data.get('bloodSugar') or patient_data.get('fastingBloodSugar') or 0)
        vitamin_d = float(patient_data.get('vitaminD') or 0)
        
        # Calculate BMI if not provided
        if bmi == 0 and height > 0 and weight > 0:
            height_m = height / 100
            bmi = round(weight / (height_m * height_m), 2)
        
        # Generate risk analysis for each condition
        vitamin_d_analysis = self._analyze_vitamin_d(
            vitamin_d, bmi, age, gender
        )
        
        diabetes_analysis = self._analyze_diabetes(
            bmi, blood_sugar, age
        )
        
        anemia_analysis = self._analyze_anemia(
            hemoglobin, gender, age
        )
        
        heart_analysis = self._analyze_heart_disease(
            systolic_bp, diastolic_bp, total_cholesterol, hdl_cholesterol, 
            smoking, bmi
        )
        
        return {
            "vitaminD": vitamin_d_analysis,
            "diabetes": diabetes_analysis,
            "anemia": anemia_analysis,
            "heartDisease": heart_analysis,
            "patientSummary": self._generate_patient_summary(patient_data)
        }
    
    def _analyze_vitamin_d(
        self, 
        vitamin_d: float, 
        bmi: float, 
        age: int, 
        gender: str
    ) -> Dict[str, Any]:
        """Analyze Vitamin D deficiency risk"""
        
        # Determine risk level based on vitamin D levels
        if vitamin_d >= 30:
            risk_level = "Low"
            risk_score = 2
        elif vitamin_d >= 20:
            risk_level = "Moderate"
            risk_score = 4
        elif vitamin_d >= 10:
            risk_level = "High"
            risk_score = 7
        else:
            risk_level = "High"
            risk_score = 9
        
        # Identify risk factors
        risk_factors = []
        if vitamin_d < 30:
            risk_factors.append("Low serum vitamin D level")
        if bmi >= 30:
            risk_factors.append("Obesity (higher risk of deficiency)")
        if age > 65:
            risk_factors.append("Advanced age (reduced skin synthesis)")
        if age > 50:
            risk_factors.append("Middle age (reduced vitamin D absorption)")
        
        # Generate recommendations
        recommended_actions = []
        if vitamin_d < 20:
            recommended_actions.extend([
                "Consult doctor for vitamin D supplementation",
                "Take vitamin D3 supplements (1000-2000 IU daily)",
                "Retest vitamin D levels in 3 months"
            ])
        elif vitamin_d < 30:
            recommended_actions.extend([
                "Increase sun exposure 20-30 minutes daily",
                "Consume vitamin D rich foods like fish, eggs, fortified milk",
                "Consider vitamin D supplements if recommended by doctor"
            ])
        
        if bmi >= 30:
            recommended_actions.append("Maintain healthy weight through diet and exercise")
        
        recommended_actions.extend([
            "Include fatty fish (salmon, mackerel) in diet",
            "Consume fortified dairy products"
        ])
        
        diet_lifestyle = [
            "Get moderate sun exposure (10-30 minutes midday)",
            "Maintain regular physical activity",
            "Follow balanced diet rich in nutrients"
        ]
        
        additional_support = [
            "Consider calcium supplementation if recommended",
            "Include dairy products and leafy greens",
            "Regular monitoring of vitamin D levels"
        ]
        
        return {
            "riskLevel": risk_level,
            "riskScore": risk_score,
            "riskFactors": risk_factors,
            "recommendedActions": recommended_actions,
            "dietLifestyle": diet_lifestyle,
            "additionalSupport": additional_support
        }
    
    def _analyze_diabetes(
        self, 
        bmi: float, 
        blood_sugar: float, 
        age: int
    ) -> Dict[str, Any]:
        """Analyze Diabetes risk"""
        
        # Determine risk level
        if blood_sugar < 100 and bmi < 25:
            risk_level = "Low"
            risk_score = 2
        elif blood_sugar < 126 and bmi < 30:
            risk_level = "Moderate"
            risk_score = 5
        elif blood_sugar < 126:
            risk_level = "Moderate"
            risk_score = 6
        else:
            risk_level = "High"
            risk_score = 8
        
        # Identify risk factors
        risk_factors = []
        if bmi >= 30:
            risk_factors.append("Obesity")
        elif bmi >= 25:
            risk_factors.append("Overweight")
        if blood_sugar >= 100:
            risk_factors.append("Elevated blood sugar")
        if age > 45:
            risk_factors.append("Advanced age")
        if age > 60:
            risk_factors.append("Senior age (higher risk)")
        
        # Generate recommendations
        recommended_actions = []
        if blood_sugar >= 126:
            recommended_actions.extend([
                "Consult healthcare provider immediately",
                "Schedule fasting blood sugar and HbA1c tests",
                "Consider diabetes medication if prescribed"
            ])
        elif blood_sugar >= 100:
            recommended_actions.extend([
                "Reduce sugar and refined carbohydrate intake",
                "Increase physical activity",
                "Monitor blood sugar levels regularly"
            ])
        
        if bmi >= 25:
            recommended_actions.append("Work towards healthy weight through diet and exercise")
        
        recommended_actions.extend([
            "Engage in regular physical activity (150 min/week)",
            "Follow low-glycemic index diet"
        ])
        
        diet_lifestyle = [
            "Reduce processed foods and added sugars",
            "Increase fiber intake (vegetables, whole grains)",
            "Maintain regular meal timing",
            "Limit alcohol consumption"
        ]
        
        additional_support = [
            "Consider consulting a dietitian",
            "Join diabetes prevention program if available",
            "Regular health check-ups"
        ]
        
        return {
            "riskLevel": risk_level,
            "riskScore": risk_score,
            "riskFactors": risk_factors,
            "recommendedActions": recommended_actions,
            "dietLifestyle": diet_lifestyle,
            "additionalSupport": additional_support
        }
    
    def _analyze_anemia(
        self, 
        hemoglobin: float, 
        gender: str, 
        age: int
    ) -> Dict[str, Any]:
        """Analyze Anemia risk"""
        
        # Normal hemoglobin values: Male: 13.5-17.5, Female: 12-16
        normal_hb_male = 13.5
        normal_hb_female = 12.0
        
        # Determine risk level
        if gender == 'female':
            if hemoglobin >= 12:
                risk_level = "Low"
                risk_score = 2
            elif hemoglobin >= 10:
                risk_level = "Moderate"
                risk_score = 5
            else:
                risk_level = "High"
                risk_score = 8
        else:
            if hemoglobin >= 13.5:
                risk_level = "Low"
                risk_score = 2
            elif hemoglobin >= 11:
                risk_level = "Moderate"
                risk_score = 5
            else:
                risk_level = "High"
                risk_score = 8
        
        # Identify risk factors
        risk_factors = []
        if gender == 'female' and hemoglobin < 12:
            risk_factors.append("Female with low hemoglobin")
        elif gender == 'male' and hemoglobin < 13.5:
            risk_factors.append("Male with low hemoglobin")
        
        if hemoglobin < 11:
            risk_factors.append("Significantly low hemoglobin levels")
        
        if age > 65:
            risk_factors.append("Advanced age (higher risk)")
        
        if gender == 'female':
            risk_factors.append("Female gender (higher anemia risk)")
        
        # Generate recommendations
        recommended_actions = []
        if hemoglobin < 10:
            recommended_actions.extend([
                "Consult healthcare provider for evaluation",
                "Request iron studies and complete blood count",
                "Consider iron supplementation if deficient"
            ])
        elif hemoglobin < 12:
            recommended_actions.extend([
                "Increase iron-rich foods in diet",
                "Consider iron supplementation",
                "Schedule follow-up blood test in 3 months"
            ])
        
        recommended_actions.extend([
            "Consume iron-rich foods (red meat, beans, leafy greens)",
            "Combine iron intake with vitamin C for better absorption",
            "Avoid coffee/tea with meals (inhibits iron absorption)"
        ])
        
        diet_lifestyle = [
            "Include iron-rich foods in diet",
            "Consume vitamin C rich foods (citrus, berries)",
            "Maintain balanced nutrition"
        ]
        
        additional_support = [
            "Consider B12 and folate supplementation if needed",
            "Include dark leafy greens in diet",
            "Regular health monitoring"
        ]
        
        return {
            "riskLevel": risk_level,
            "riskScore": risk_score,
            "riskFactors": risk_factors,
            "recommendedActions": recommended_actions,
            "dietLifestyle": diet_lifestyle,
            "additionalSupport": additional_support
        }
    
    def _analyze_heart_disease(
        self,
        systolic_bp: int,
        diastolic_bp: int,
        total_cholesterol: float,
        hdl_cholesterol: float,
        smoking: str,
        bmi: float
    ) -> Dict[str, Any]:
        """Analyze Heart Disease / Hypertension risk"""
        
        # Calculate risk score components
        bp_score = 0
        cholesterol_score = 0
        lifestyle_score = 0
        
        # Blood Pressure scoring
        if systolic_bp >= 180 or diastolic_bp >= 120:
            bp_score = 3
        elif systolic_bp >= 140 or diastolic_bp >= 90:
            bp_score = 2
        elif systolic_bp >= 130 or diastolic_bp >= 80:
            bp_score = 1
        
        # Cholesterol scoring
        if total_cholesterol >= 240:
            cholesterol_score = 3
        elif total_cholesterol >= 200:
            cholesterol_score = 2
        
        if hdl_cholesterol < 40:
            cholesterol_score += 1
        
        # Lifestyle scoring
        if smoking == 'yes':
            lifestyle_score += 2
        if bmi >= 30:
            lifestyle_score += 1
        
        # Calculate total risk score (out of 10)
        total_score = bp_score + cholesterol_score + lifestyle_score
        total_score = min(total_score, 10)
        
        # Determine risk level
        if total_score <= 3:
            risk_level = "Low"
        elif total_score <= 6:
            risk_level = "Moderate"
        else:
            risk_level = "High"
        
        # Identify risk factors
        risk_factors = []
        if systolic_bp >= 140 or diastolic_bp >= 90:
            risk_factors.append("Hypertension (high blood pressure)")
        elif systolic_bp >= 130 or diastolic_bp >= 80:
            risk_factors.append("Elevated blood pressure")
        
        if total_cholesterol >= 200:
            risk_factors.append("High cholesterol")
        
        if hdl_cholesterol < 40:
            risk_factors.append("Low HDL (good) cholesterol")
        
        if smoking == 'yes':
            risk_factors.append("Smoking")
        
        if bmi >= 30:
            risk_factors.append("Obesity")
        
        # Generate recommendations
        recommended_actions = []
        if systolic_bp >= 140 or diastolic_bp >= 90:
            recommended_actions.extend([
                "Consult cardiologist",
                "Monitor blood pressure regularly",
                "Consider blood pressure medication if prescribed"
            ])
        
        if total_cholesterol >= 200:
            recommended_actions.extend([
                "Reduce saturated and trans fat intake",
                "Consider cholesterol screening",
                "Discuss statin therapy with doctor if needed"
            ])
        
        if smoking == 'yes':
            recommended_actions.append("Quit smoking - seek support if needed")
        
        if bmi >= 30:
            recommended_actions.append("Work towards healthy weight")
        
        recommended_actions.extend([
            "Exercise regularly (150 minutes moderate activity weekly)",
            "Reduce sodium intake",
            "Manage stress levels"
        ])
        
        diet_lifestyle = [
            "Follow heart-healthy diet (Mediterranean or DASH)",
            "Increase physical activity",
            "Limit processed foods",
            "Reduce alcohol consumption"
        ]
        
        additional_support = [
            "Consider omega-3 fatty acid supplementation",
            "Regular cardiovascular health check-ups",
            "Maintain healthy sleep patterns"
        ]
        
        return {
            "riskLevel": risk_level,
            "riskScore": total_score,
            "riskFactors": risk_factors,
            "recommendedActions": recommended_actions,
            "dietLifestyle": diet_lifestyle,
            "additionalSupport": additional_support
        }
    
    def _generate_patient_summary(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate patient summary from data"""
        return {
            "age": patient_data.get('age'),
            "gender": patient_data.get('gender'),
            "bmi": patient_data.get('bmi'),
            "dateGenerated": self._get_current_timestamp()
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Singleton instance
_recommendation_generator = None


def get_recommendation_generator() -> RecommendationGenerator:
    """Get or create recommendation generator instance"""
    global _recommendation_generator
    if _recommendation_generator is None:
        _recommendation_generator = RecommendationGenerator()
    return _recommendation_generator


def generate_health_recommendations(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to generate health recommendations
    
    Args:
        patient_data: Dictionary containing patient health parameters
        
    Returns:
        Dictionary with risk analysis and recommendations
    """
    generator = get_recommendation_generator()
    return generator.analyze_patient(patient_data)

