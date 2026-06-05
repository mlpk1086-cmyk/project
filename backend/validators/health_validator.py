"""
Health Data Validators
Pydantic models for validating health-related requests
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator


# Valid enum values
GENDER_VALUES = ['male', 'female', 'other', 'prefer_not_to_say']
LOCATION_VALUES = ['urban', 'rural', 'suburban', 'northern', 'southern', 'tropical', 'temperate']
SMOKING_VALUES = ['yes', 'no', 'former', 'never']
PHYSICAL_ACTIVITY_VALUES = ['none', 'sedentary', 'occasional', 'moderate', 'active']
ALCOHOL_VALUES = ['none', 'occasional', 'moderate', 'heavy']


class HealthDataValidator(BaseModel):
    """Validator for health data submission"""
    
    # Demographics (all optional but validated when provided)
    age: Optional[int] = Field(None, ge=0, le=150, description="Age in years")
    height: Optional[float] = Field(None, ge=30, le=300, description="Height in cm")
    weight: Optional[float] = Field(None, ge=10, le=500, description="Weight in kg")
    gender: Optional[str] = Field(None, description="Gender")
    location: Optional[str] = Field(None, max_length=255, description="Location")
    
    # Vital signs
    systolic_bp: Optional[int] = Field(None, ge=60, le=250, description="Systolic blood pressure (mmHg)")
    diastolic_bp: Optional[int] = Field(None, ge=40, le=150, description="Diastolic blood pressure (mmHg)")
    heart_rate: Optional[int] = Field(None, ge=30, le=250, description="Heart rate (bpm)")
    
    # Cholesterol
    total_cholesterol: Optional[float] = Field(None, ge=50, le=400, description="Total cholesterol (mg/dL)")
    hdl_cholesterol: Optional[float] = Field(None, ge=10, le=150, description="HDL cholesterol (mg/dL)")
    
    # Blood tests
    hemoglobin: Optional[float] = Field(None, ge=3, le=20, description="Hemoglobin (g/dL)")
    vitamin_d: Optional[float] = Field(None, ge=0, le=200, description="Vitamin D (ng/mL)")
    fasting_blood_sugar: Optional[float] = Field(None, ge=20, le=500, description="Fasting blood sugar (mg/dL)")
    iron_percent_rda: Optional[float] = Field(None, ge=0, le=200, description="Iron (% RDA)")
    
    # Lifestyle
    smoking_status: Optional[str] = Field(None, description="Smoking status")
    physical_activity: Optional[str] = Field(None, description="Physical activity level")
    alcohol_consumption: Optional[str] = Field(None, description="Alcohol consumption")
    exercise_level: Optional[str] = Field(None, description="Exercise level")
    
    # Additional fields
    hemoglobin_gdl: Optional[float] = Field(None, alias='hemoglobinGdl', description="Hemoglobin (g/dL) alias")
    serum_vitamin_d_ngml: Optional[float] = Field(None, alias='serumVitaminDNgml', description="Serum Vitamin D (ng/mL)")
    blood_sugar: Optional[float] = Field(None, alias='BloodSugar', description="Blood sugar alias")
    hba1c_level: Optional[float] = Field(None, alias='hbA1cLevel', description="HbA1c level")
    iron_intake: Optional[str] = Field(None, description="Iron intake")
    vitamin_b12_level: Optional[float] = Field(None, description="Vitamin B12 level")
    sun_exposure: Optional[float] = Field(None, ge=0, le=24, description="Sun exposure (hours/day)")
    vitamin_d_percent_rda: Optional[float] = Field(None, description="Vitamin D (% RDA)")
    calcium_percent_rda: Optional[float] = Field(None, description="Calcium (% RDA)")
    diet_type: Optional[str] = Field(None, description="Diet type")
    
    @validator('gender')
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower().strip()
            if v not in GENDER_VALUES:
                v = None  # Allow unknown values but normalize
        return v
    
    @validator('smoking_status')
    def validate_smoking(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower().strip()
            if v not in SMOKING_VALUES:
                v = 'no'
        return v
    
    @validator('physical_activity')
    def validate_physical_activity(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower().strip()
            if v not in PHYSICAL_ACTIVITY_VALUES:
                v = 'occasional'
        return v
    
    @validator('alcohol_consumption')
    def validate_alcohol(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower().strip()
            if v not in ALCOHOL_VALUES:
                v = 'none'
        return v
    
    @validator('exercise_level')
    def validate_exercise_level(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower().strip()
            if v not in PHYSICAL_ACTIVITY_VALUES:
                v = 'occasional'
        return v
    
    @validator('location')
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower().strip()
        return v
    
    @validator('bmi', always_run=True)
    def calculate_bmi(cls, v, values):
        """Calculate BMI if height and weight are provided"""
        height = values.get('height')
        weight = values.get('weight')
        
        if height and weight and height > 0 and weight > 0:
            height_m = height / 100
            bmi = round(weight / (height_m * height_m), 2)
            return bmi
        return v or 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary with camelCase keys"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        
        # Add BMI calculation
        if self.height and self.weight and self.height > 0 and self.weight > 0:
            height_m = self.height / 100
            data['bmi'] = round(self.weight / (height_m * height_m), 2)
        
        return data
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "age": 35,
                "height": 175,
                "weight": 70,
                "gender": "male",
                "location": "urban",
                "systolicBP": 120,
                "diastolicBP": 80,
                "heartRate": 72,
                "totalCholesterol": 200,
                "hdlCholesterol": 50,
                "hemoglobin": 14.5,
                "vitaminD": 30,
                "fastingBloodSugar": 95,
                "smokingStatus": "no",
                "physicalActivity": "moderate"
            }
        }


class RiskAssessmentValidator(BaseModel):
    """Validator for risk assessment requests"""
    
    disease: str = Field(..., description="Disease name")
    risk_level: Optional[str] = Field('low', description="Risk level")
    
    @validator('disease')
    def validate_disease(cls, v: str) -> str:
        valid_diseases = ['diabetes', 'anemia', 'vitamind', 'heart']
        v = v.lower().strip()
        if v not in valid_diseases:
            raise ValueError(f'Disease must be one of: {valid_diseases}')
        return v
    
    @validator('risk_level')
    def validate_risk_level(cls, v: str) -> str:
        valid_levels = ['low', 'moderate', 'high']
        v = v.lower().strip()
        if v not in valid_levels:
            v = 'low'
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "disease": "diabetes",
                "risk_level": "moderate"
            }
        }


class MLInputValidator(BaseModel):
    """Validator for ML model input"""
    
    age: int = Field(..., ge=0, le=150, description="Age in years")
    bmi: float = Field(..., ge=10, le=60, description="BMI")
    gender: str = Field(..., description="Gender")
    systolic_bp: int = Field(..., ge=60, le=250, description="Systolic BP")
    diastolic_bp: int = Field(..., ge=40, le=150, description="Diastolic BP")
    total_cholesterol: float = Field(..., ge=50, le=400, description="Total cholesterol")
    hdl_cholesterol: float = Field(..., ge=10, le=150, description="HDL cholesterol")
    hemoglobin: float = Field(..., ge=3, le=20, description="Hemoglobin")
    vitamin_d: float = Field(..., ge=0, le=200, description="Vitamin D")
    fasting_blood_sugar: float = Field(..., ge=20, le=500, description="Fasting blood sugar")
    smoking_status: str = Field(..., description="Smoking status")
    physical_activity: str = Field(..., description="Physical activity")
    location: Optional[str] = Field(None, description="Location")
    alcohol_consumption: Optional[str] = Field(None, description="Alcohol consumption")
    exercise_level: Optional[str] = Field(None, description="Exercise level")
    iron_percent_rda: Optional[float] = Field(None, description="Iron (% RDA)")
    
    @validator('gender', 'smoking_status', 'physical_activity')
    def normalize_values(cls, v: str) -> str:
        return v.lower().strip() if v else 'unknown'
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 35,
                "bmi": 25.5,
                "gender": "male",
                "systolicBP": 120,
                "diastolicBP": 80,
                "totalCholesterol": 200,
                "hdlCholesterol": 50,
                "hemoglobin": 14.5,
                "vitaminD": 30,
                "fastingBloodSugar": 95,
                "smokingStatus": "no",
                "physicalActivity": "moderate"
            }
        }


class SimilarPatientsValidator(BaseModel):
    """Validator for similar patients request"""
    
    top_n: Optional[int] = Field(5, ge=1, le=20, description="Number of similar patients")
    include_history: Optional[bool] = Field(False, description="Include patient history")
    
    class Config:
        json_schema_extra = {
            "example": {
                "top_n": 5,
                "include_history": False
            }
        }


class TrainModelValidator(BaseModel):
    """Validator for model training request"""
    
    file_path: str = Field(..., description="Path to training data file")
    model_types: Optional[List[str]] = Field(
        ['random_forest'], 
        description="Types of models to train"
    )
    test_size: Optional[float] = Field(0.2, ge=0.1, le=0.4, description="Test set proportion")
    
    @validator('model_types')
    def validate_model_types(cls, v: List[str]) -> List[str]:
        valid_types = ['random_forest', 'gradient_boosting']
        return [m.lower() for m in v if m.lower() in valid_types] or ['random_forest']
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/data/training_data.csv",
                "model_types": ["random_forest", "gradient_boosting"],
                "test_size": 0.2
            }
        }

