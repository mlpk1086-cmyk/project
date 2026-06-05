 """
Train Vitamin D Risk Model
Train ML model using the Vitamin D dataset
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

# Dataset path
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'Vitimin D.xlsx')
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

def load_and_prepare_data():
    """Load and prepare the Vitamin D dataset"""
    # Load dataset
    df = pd.read_excel(DATASET_PATH)
    
    print(f"Loaded dataset with {len(df)} records")
    print(f"Columns: {df.columns.tolist()}")
    
    # Create vitamin D risk target based on serum vitamin D levels
    # Deficient: < 20 ng/mL
    # Insufficient: 20-30 ng/mL
    # Sufficient: 30-100 ng/mL
    # Toxic: > 100 ng/mL
    
    def classify_vitamin_d(value):
        if pd.isna(value):
            return 'unknown'
        elif value < 10:
            return 'high'  # Severe deficiency
        elif value < 20:
            return 'high'  # Deficiency
        elif value < 30:
            return 'moderate'  # Insufficient
        else:
            return 'low'  # Sufficient
    
    df['vitamin_d_risk'] = df['serum_vitamin_d_ng_ml'].apply(classify_vitamin_d)
    
    print(f"\nRisk distribution:")
    print(df['vitamin_d_risk'].value_counts())
    
    return df

def preprocess_data(df):
    """Preprocess the data for training"""
    df = df.copy()
    
    # Handle missing values in alcohol_consumption
    df['alcohol_consumption'] = df['alcohol_consumption'].fillna('Unknown')
    
    # Convert categorical columns to lowercase
    categorical_cols = ['gender', 'smoking_status', 'alcohol_consumption', 
                       'exercise_level', 'diet_type', 'sun_exposure',
                       'income_level', 'latitude_region']
    
    label_encoders = {}
    
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower()
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
    
    # Store feature columns
    feature_columns = [col for col in df.columns if col not in ['vitamin_d_risk', 'serum_vitamin_d_ng_ml']]
    
    # Prepare features and target
    X = df[feature_columns]
    y = df['vitamin_d_risk']
    
    # Encode target
    target_encoder = LabelEncoder()
    y_encoded = target_encoder.fit_transform(y)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"\nFeature columns: {feature_columns}")
    print(f"Target classes: {target_encoder.classes_}")
    
    return X_scaled, y_encoded, feature_columns, label_encoders, target_encoder, scaler

def train_models(X, y, feature_columns):
    """Train Random Forest and Gradient Boosting models"""
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    results = {}
    
    # Train Random Forest
    print("\n" + "="*50)
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    
    rf_accuracy = accuracy_score(y_test, rf_pred)
    rf_precision = precision_score(y_test, rf_pred, average='weighted', zero_division=0)
    rf_recall = recall_score(y_test, rf_pred, average='weighted', zero_division=0)
    rf_f1 = f1_score(y_test, rf_pred, average='weighted', zero_division=0)
    
    # Cross-validation
    rf_cv = cross_val_score(rf_model, X, y, cv=5)
    
    results['random_forest'] = {
        'accuracy': rf_accuracy,
        'precision': rf_precision,
        'recall': rf_recall,
        'f1': rf_f1,
        'cv_mean': rf_cv.mean(),
        'cv_std': rf_cv.std()
    }
    
    print(f"Random Forest Results:")
    print(f"  Accuracy: {rf_accuracy:.4f}")
    print(f"  F1 Score: {rf_f1:.4f}")
    print(f"  CV Mean: {rf_cv.mean():.4f} (+/- {rf_cv.std():.4f})")
    
    # Feature importance
    print("\nTop 10 Feature Importances (Random Forest):")
    importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(importance.head(10).to_string(index=False))
    
    # Train Gradient Boosting
    print("\n" + "="*50)
    print("Training Gradient Boosting...")
    gb_model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    gb_model.fit(X_train, y_train)
    gb_pred = gb_model.predict(X_test)
    
    gb_accuracy = accuracy_score(y_test, gb_pred)
    gb_precision = precision_score(y_test, gb_pred, average='weighted', zero_division=0)
    gb_recall = recall_score(y_test, gb_pred, average='weighted', zero_division=0)
    gb_f1 = f1_score(y_test, gb_pred, average='weighted', zero_division=0)
    
    gb_cv = cross_val_score(gb_model, X, y, cv=5)
    
    results['gradient_boosting'] = {
        'accuracy': gb_accuracy,
        'precision': gb_precision,
        'recall': gb_recall,
        'f1': gb_f1,
        'cv_mean': gb_cv.mean(),
        'cv_std': gb_cv.std()
    }
    
    print(f"Gradient Boosting Results:")
    print(f"  Accuracy: {gb_accuracy:.4f}")
    print(f"  F1 Score: {gb_f1:.4f}")
    print(f"  CV Mean: {gb_cv.mean():.4f} (+/- {gb_cv.std():.4f})")
    
    # Select best model
    best_model_name = 'random_forest' if rf_f1 >= gb_f1 else 'gradient_boosting'
    best_model = rf_model if best_model_name == 'random_forest' else gb_model
    
    print(f"\nBest Model: {best_model_name}")
    
    return rf_model, gb_model, results, best_model_name

def save_models(rf_model, gb_model, label_encoders, target_encoder, scaler, feature_columns, results):
    """Save all models and preprocessors"""
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    saved_files = []
    
    # Save Random Forest
    rf_path = os.path.join(MODELS_DIR, 'vitamin_d_risk_random_forest.joblib')
    joblib.dump(rf_model, rf_path)
    saved_files.append(rf_path)
    print(f"Saved Random Forest to {rf_path}")
    
    # Save Gradient Boosting
    gb_path = os.path.join(MODELS_DIR, 'vitamin_d_risk_gradient_boosting.joblib')
    joblib.dump(gb_model, gb_path)
    saved_files.append(gb_path)
    print(f"Saved Gradient Boosting to {gb_path}")
    
    # Save label encoders
    encoders_path = os.path.join(MODELS_DIR, 'vitamin_d_label_encoders.joblib')
    joblib.dump(label_encoders, encoders_path)
    saved_files.append(encoders_path)
    
    # Save target encoder
    target_path = os.path.join(MODELS_DIR, 'vitamin_d_target_encoder.joblib')
    joblib.dump(target_encoder, target_path)
    saved_files.append(target_path)
    
    # Save scaler
    scaler_path = os.path.join(MODELS_DIR, 'vitamin_d_scaler.joblib')
    joblib.dump(scaler, scaler_path)
    saved_files.append(scaler_path)
    
    # Save feature columns
    features_path = os.path.join(MODELS_DIR, 'vitamin_d_features.json')
    with open(features_path, 'w') as f:
        json.dump(feature_columns, f)
    saved_files.append(features_path)
    
    # Save metrics
    metrics_path = os.path.join(MODELS_DIR, 'vitamin_d_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(results, f, indent=2)
    saved_files.append(metrics_path)
    
    return saved_files

def generate_recommendations_from_model(patient_data, risk_level):
    """Generate recommendations based on ML model prediction"""
    
    recommendations = {
        'high': {
            'title': 'High Vitamin D Deficiency Risk',
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
                'Consider UV lamp therapy',
                'Take Vitamin D supplements as prescribed',
                'Regular blood testing every 3 months'
            ]
        },
        'moderate': {
            'title': 'Moderate Vitamin D Insufficiency',
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
    
    return recommendations.get(risk_level, recommendations['low'])

def main():
    """Main training function"""
    print("="*60)
    print("Vitamin D Risk Model Training")
    print("="*60)
    
    # Load and prepare data
    df = load_and_prepare_data()
    
    # Preprocess
    X, y, feature_columns, label_encoders, target_encoder, scaler = preprocess_data(df)
    
    # Train models
    rf_model, gb_model, results, best_model_name = train_models(X, y, feature_columns)
    
    # Save models
    saved_files = save_models(rf_model, gb_model, label_encoders, target_encoder, scaler, feature_columns, results)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"\nSaved {len(saved_files)} files:")
    for f in saved_files:
        print(f"  - {f}")
    
    # Test prediction
    print("\n" + "="*60)
    print("Testing Model Prediction...")
    print("="*60)
    
    # Sample patient data
    sample_data = {
        'age': 35,
        'gender': 0,  # encoded
        'bmi': 25.0,
        'smoking_status': 0,
        'alcohol_consumption': 0,
        'exercise_level': 1,
        'diet_type': 1,
        'sun_exposure': 1,
        'income_level': 1,
        'latitude_region': 1,
        'vitamin_a_percent_rda': 80.0,
        'vitamin_c_percent_rda': 90.0,
        'vitamin_d_percent_rda': 50.0,
        'vitamin_e_percent_rda': 85.0,
        'vitamin_b12_percent_rda': 75.0,
        'folate_percent_rda': 80.0,
        'calcium_percent_rda': 70.0,
        'iron_percent_rda': 85.0,
        'hemoglobin_g_dl': 14.0,
        'serum_vitamin_b12_pg_ml': 300.0
    }
    
    # Scale and predict
    sample_df = pd.DataFrame([sample_data])[feature_columns]
    sample_scaled = scaler.transform(sample_df)
    prediction = rf_model.predict(sample_scaled)[0]
    risk_level = target_encoder.inverse_transform([prediction])[0]
    
    print(f"\nSample prediction: {risk_level}")
    print(f"Recommendations: {generate_recommendations_from_model(sample_data, risk_level)['title']}")

if __name__ == '__main__':
    main()

