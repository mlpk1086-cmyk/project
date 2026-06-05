"""
Data preprocessing module for healthcare ML models
Handles data cleaning, feature engineering, and normalization
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import json
import os

class HealthcareDataPreprocessor:
    """Handles preprocessing of healthcare data for ML models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        self.is_fitted = False
        
    def load_dataset(self, file_path):
        """Load dataset from CSV file"""
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            raise ValueError(f"Error loading dataset: {str(e)}")
    
    def validate_dataset(self, df):
        """Validate that dataset has required columns"""
        required_columns = ['age', 'bmi']
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return True
    
    def clean_data(self, df):
        """Clean and preprocess the data"""
        df = df.copy()
        
        # Convert all columns to lowercase for consistency
        df.columns = df.columns.str.lower().str.strip()
        
        # Handle missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
        
        # Handle categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna('unknown')
            df[col] = df[col].str.lower().str.strip()
        
        return df
    
    def encode_categorical(self, df, fit=True):
        """Encode categorical variables"""
        df = df.copy()
        
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            
            if fit:
                # Check if already fitted
                if hasattr(self.label_encoders[col], 'classes_') and len(self.label_encoders[col].classes_) > 0:
                    # Already fitted, handle unseen labels
                    known_labels = set(self.label_encoders[col].classes_)
                    df[col] = df[col].apply(
                        lambda x, known=known_labels: x if x in known else list(known)[0]
                    )
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                # Transform mode - handle unseen labels
                if hasattr(self.label_encoders[col], 'classes_') and len(self.label_encoders[col].classes_) > 0:
                    known_labels = set(self.label_encoders[col].classes_)
                    df[col] = df[col].apply(
                        lambda x, known=known_labels: x if x in known else list(known)[0]
                    )
                    df[col] = self.label_encoders[col].transform(df[col])
                else:
                    # Not fitted yet, fit now
                    df[col] = self.label_encoders[col].fit_transform(df[col])
        
        return df
    
    def create_features(self, df):
        """Create additional features from raw data"""
        df = df.copy()
        
        # BMI categories
        if 'bmi' in df.columns:
            df['bmi_category'] = pd.cut(
                df['bmi'], 
                bins=[0, 18.5, 25, 30, 35, 100],
                labels=[0, 1, 2, 3, 4]
            )
        
        # Age groups
        if 'age' in df.columns:
            df['age_group'] = pd.cut(
                df['age'],
                bins=[0, 30, 45, 60, 75, 100],
                labels=[0, 1, 2, 3, 4]
            )
        
        # Blood pressure categories
        if 'systolicbp' in df.columns and 'diastolicbp' in df.columns:
            df['bp_category'] = df.apply(
                lambda row: self._categorize_bp(
                    row.get('systolicbp', 120), 
                    row.get('diastolicbp', 80)
                ), 
                axis=1
            )
        
        return df
    
    def _categorize_bp(self, systolic, diastolic):
        """Categorize blood pressure"""
        if systolic >= 140 or diastolic >= 90:
            return 2  # High
        elif systolic >= 120 or diastolic >= 80:
            return 1  # Elevated
        return 0  # Normal
    
    def prepare_features(self, df, target_columns=None):
        """Prepare features for ML model"""
        df = df.copy()
        
        # Clean data
        df = self.clean_data(df)
        
        # Create features
        df = self.create_features(df)
        
        # Remove target columns from features if specified
        if target_columns:
            for col in target_columns:
                if col in df.columns:
                    df = df.drop(columns=[col])
        
        # Encode categorical variables
        df = self.encode_categorical(df, fit=self.is_fitted)
        
        # Store feature columns
        self.feature_columns = df.columns.tolist()
        
        return df
    
    def fit_transform(self, df, target_columns=None):
        """Fit and transform the data"""
        df = self.prepare_features(df, target_columns)
        self.is_fitted = True
        
        # Scale numerical features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = self.scaler.fit_transform(df[numeric_cols])
        
        return df
    
    def transform(self, df):
        """Transform new data using fitted preprocessor"""
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted yet")
        
        df = self.prepare_features(df)
        
        # Scale numerical features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = self.scaler.transform(df[numeric_cols])
        
        return df
    
    def get_feature_names(self):
        """Get list of feature names"""
        return self.feature_columns
    
    def save(self, path):
        """Save preprocessor to file"""
        import joblib
        joblib.dump(self, path)
    
    @classmethod
    def load(cls, path):
        """Load preprocessor from file"""
        import joblib
        return joblib.load(path)


def preprocess_health_data(data_dict, preprocessor=None):
    """Preprocess single health data record for prediction"""
    # Convert to DataFrame
    df = pd.DataFrame([data_dict])
    
    # Use preprocessor if provided
    if preprocessor:
        return preprocessor.transform(df)
    
    # Otherwise, do basic preprocessing
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()
    
    # Fill missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df


def get_sample_dataset_info():
    """Return information about expected dataset format"""
    return {
        "required_columns": [
            "age", "bmi", "gender", "systolicbp", "diastolicbp",
            "heartrate", "totalcholesterol", "hdlcholesterol",
            "hemoglobin", "fastingbloodsugar",
            "smoking"
        ],
        "target_columns": [
            "diabetes_risk", "anemia_risk", "heart_risk", "vitamind_risk"
        ],
        "description": "Dataset should contain health metrics and risk labels for training"
    }


def extract_risk_from_recommendations(df):
    """
    Extract risk levels from Dynamic_Recommendations column
    """
    df = df.copy()
    
    # Initialize risk columns with 'low' as default
    df['diabetes_risk'] = 'low'
    df['anemia_risk'] = 'low'
    df['heart_risk'] = 'low'
    df['vitamind_risk'] = 'low'
    
    # Keywords that indicate higher risk
    risk_keywords = {
        'diabetes_risk': ['diabetes', 'blood sugar', 'glucose', 'reduce weight'],
        'anemia_risk': ['anemia', 'iron', 'protein', 'hemoglobin'],
        'heart_risk': ['heart', 'bp', 'blood pressure', 'cholesterol', 'salt'],
        'vitamind_risk': ['sun', 'vitamin d', 'safe sun']
    }
    
    for idx, row in df.iterrows():
        rec = str(row.get('Dynamic_Recommendations', '')).lower()
        
        # Check for each risk type
        for risk_type, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in rec:
                    # If recommendation mentions it, set risk to moderate
                    df.at[idx, risk_type] = 'moderate'
                    break
    
    return df


def load_xlsx_dataset(file_path):
    """
    Load dataset from XLSX file with proper column mapping
    Handles the Structured_Healthcare_With_Separate_Recommendations.xlsx format
    """
    try:
        df = pd.read_excel(file_path)
        
        # Map XLSX columns to standardized format
        column_mapping = {
            'Age': 'age',
            'Gender': 'gender',
            'BMI': 'bmi',
            'Systolic BP': 'systolicbp',
            'Systolic_BP': 'systolicbp',
            'Diastolic BP': 'diastolicbp',
            'Diastolic_BP': 'diastolicbp',
            'Total Cholesterol': 'totalcholesterol',
            'HDL': 'hdlcholesterol',
            'HDL_Cholesterol': 'hdlcholesterol',
            'Hemoglobin': 'hemoglobin',
            'Blood Sugar': 'fastingbloodsugar',
            'Smoking': 'smokingstatus',
            'Smoking_Status': 'smokingstatus',
            'Sun_Exposure (hrs/week)': 'sunexposure',
            'Vitamin D Risk': 'vitamind_risk',
            'Vitamin D Recommendation': 'vitamind_recommendation',
            'Anemia Risk': 'anemia_risk',
            'Anemia Recommendation': 'anemia_recommendation',
            'Diabetes Risk': 'diabetes_risk',
            'Diabetes Recommendation': 'diabetes_recommendation',
            'Heart Risk': 'heart_risk',
            'Heart Recommendation': 'heart_recommendation',
            'Location (India - Town/City)': 'location',
            'Height (cm)': 'height',
            'Weight (kg)': 'weight'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Convert gender to lowercase
        if 'gender' in df.columns:
            df['gender'] = df['gender'].str.lower()
        
        # Convert smoking to lowercase
        if 'smokingstatus' in df.columns:
            df['smokingstatus'] = df['smokingstatus'].str.lower()
            df['smokingstatus'] = df['smokingstatus'].map({'yes': 'yes', 'no': 'no', 'Yes': 'yes', 'No': 'no'})
        
        # Convert risk levels to lowercase
        risk_columns = ['vitamind_risk', 'anemia_risk', 'diabetes_risk', 'heart_risk']
        for col in risk_columns:
            if col in df.columns:
                df[col] = df[col].str.lower()
        
        # Extract target columns from Dynamic_Recommendations if present
        if 'Dynamic_Recommendations' in df.columns:
            df = extract_risk_from_recommendations(df)
        
        return df
        
    except Exception as e:
        raise ValueError(f"Error loading XLSX dataset: {str(e)}")


def get_xlsx_column_mapping():
    """Return the column mapping for XLSX files"""
    return {
        'Age': 'age',
        'Gender': 'gender',
        'BMI': 'bmi',
        'Systolic BP': 'systolicbp',
        'Diastolic BP': 'diastolicbp',
        'Total Cholesterol': 'totalcholesterol',
        'HDL': 'hdlcholesterol',
        'Hemoglobin': 'hemoglobin',
        'Blood Sugar': 'fastingbloodsugar',
        'Smoking': 'smokingstatus',
        'Vitamin D Risk': 'vitamind_risk',
        'Vitamin D Recommendation': 'vitamind_recommendation',
        'Anemia Risk': 'anemia_risk',
        'Anemia Recommendation': 'anemia_recommendation',
        'Diabetes Risk': 'diabetes_risk',
        'Diabetes Recommendation': 'diabetes_recommendation',
        'Heart Risk': 'heart_risk',
        'Heart Recommendation': 'heart_recommendation'
    }


def generate_sample_dataset():
    """Generate a sample dataset for download as template"""
    import pandas as pd
    
    # Sample data with various health scenarios
    data = {
        'age': [25, 35, 45, 55, 65, 30, 40, 50, 60, 28],
        'bmi': [22, 26, 28, 32, 35, 24, 29, 31, 28, 21],
        'gender': ['male', 'female', 'male', 'female', 'male', 'female', 'male', 'female', 'male', 'female'],
        'systolicbp': [115, 125, 135, 145, 160, 110, 130, 140, 150, 112],
        'diastolicbp': [75, 82, 88, 92, 100, 72, 85, 90, 95, 74],
        'heartrate': [72, 78, 80, 85, 90, 68, 76, 82, 88, 70],
        'totalcholesterol': [180, 200, 220, 245, 260, 175, 210, 235, 250, 170],
        'hdlcholesterol': [55, 50, 45, 40, 35, 58, 48, 42, 38, 60],
        'hemoglobin': [15, 13, 14, 12, 11, 14, 13, 12, 11, 14],
        'vitamind': [35, 25, 20, 15, 10, 40, 22, 18, 12, 38],
        'fastingbloodsugar': [85, 95, 110, 125, 140, 80, 100, 115, 130, 82],
        'smokingstatus': ['no', 'no', 'yes', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no'],
        'physicalactivity': ['regular', 'occasional', 'none', 'occasional', 'none', 'regular', 'occasional', 'none', 'occasional', 'regular'],
        'location': ['temperate', 'temperate', 'northern', 'tropical', 'northern', 'temperate', 'temperate', 'northern', 'tropical', 'temperate'],
        'diabetes_risk': ['low', 'low', 'moderate', 'high', 'high', 'low', 'moderate', 'moderate', 'high', 'low'],
        'anemia_risk': ['low', 'moderate', 'low', 'high', 'high', 'low', 'moderate', 'moderate', 'high', 'low'],
        'heart_risk': ['low', 'low', 'moderate', 'high', 'high', 'low', 'moderate', 'moderate', 'high', 'low'],
        'vitamind_risk': ['low', 'moderate', 'high', 'high', 'high', 'low', 'moderate', 'high', 'high', 'low']
    }
    
    df = pd.DataFrame(data)
    return df
