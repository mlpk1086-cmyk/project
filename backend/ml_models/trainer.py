"""
ML Model Trainer for Healthcare Recommendation System
Handles model training, evaluation, and persistence
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from .preprocessing import HealthcareDataPreprocessor

class HealthRiskTrainer:
    """Trainer class for healthcare risk prediction models"""
    
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.preprocessor = HealthcareDataPreprocessor()
        self.models = {}
        self.model_metrics = {}
        self.target_columns = ['diabetes_risk', 'anemia_risk', 'heart_risk', 'vitamind_risk']
        
        # Create models directory if not exists
        os.makedirs(models_dir, exist_ok=True)
    
    def load_dataset(self, file_path):
        """Load dataset from CSV or Excel file"""
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            return df
        except Exception as e:
            raise ValueError(f"Error loading dataset: {str(e)}")
    
    def prepare_data(self, df, test_size=0.2, random_state=42):
        """Prepare data for training"""
        # Separate features and targets
        X = df.copy()
        y = {}
        
        for target in self.target_columns:
            if target in X.columns:
                y[target] = X[target]
                X = X.drop(columns=[target])
        
        # Fit preprocessor and transform features
        X_processed = self.preprocessor.fit_transform(X)
        
        return X_processed, y, test_size, random_state
    
    def train_model(self, X, y, model_type='random_forest', cv=5):
        """Train a single model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Initialize model
        if model_type == 'random_forest':
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'logistic_regression':
            model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='multinomial'
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=cv)
        metrics['cv_mean'] = cv_scores.mean()
        metrics['cv_std'] = cv_scores.std()
        
        return model, metrics
    
    def train_all_models(self, df, model_types=None):
        """Train models for all target variables"""
        if model_types is None:
            model_types = ['random_forest']
        
        # Prepare data
        X, y_dict, test_size, random_state = self.prepare_data(df)
        
        results = {
            'training_date': datetime.now().isoformat(),
            'dataset_size': len(df),
            'features': self.preprocessor.get_feature_names(),
            'models': {}
        }
        
        # Train model for each target
        for target in self.target_columns:
            if target not in y_dict:
                continue
            
            y = y_dict[target]
            
            # Skip if target has only one class
            if y.nunique() < 2:
                results['models'][target] = {
                    'error': f'Not enough classes in {target}',
                    'status': 'skipped'
                }
                continue
            
            target_results = {}
            
            for model_type in model_types:
                try:
                    model, metrics = self.train_model(X, y, model_type)
                    
                    # Store model
                    model_key = f"{target}_{model_type}"
                    self.models[model_key] = model
                    self.model_metrics[model_key] = metrics
                    
                    target_results[model_type] = {
                        'metrics': metrics,
                        'status': 'trained'
                    }
                    
                except Exception as e:
                    target_results[model_type] = {
                        'error': str(e),
                        'status': 'failed'
                    }
            
            results['models'][target] = target_results
        
        results['preprocessor'] = 'fitted'
        
        return results
    
    def save_models(self, prefix='health_risk'):
        """Save all trained models and preprocessor"""
        saved_files = []
        
        # Save preprocessor
        preprocessor_path = os.path.join(self.models_dir, f'{prefix}_preprocessor.joblib')
        self.preprocessor.save(preprocessor_path)
        saved_files.append(preprocessor_path)
        
        # Save models
        for model_key, model in self.models.items():
            model_path = os.path.join(self.models_dir, f'{prefix}_{model_key}.joblib')
            joblib.dump(model, model_path)
            saved_files.append(model_path)
        
        # Save metrics
        metrics_path = os.path.join(self.models_dir, f'{prefix}_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(self.model_metrics, f, indent=2)
        saved_files.append(metrics_path)
        
        return saved_files
    
    def load_models(self, prefix='health_risk'):
        """Load trained models and preprocessor"""
        # Load preprocessor
        preprocessor_path = os.path.join(self.models_dir, f'{prefix}_preprocessor.joblib')
        if os.path.exists(preprocessor_path):
            self.preprocessor = HealthcareDataPreprocessor.load(preprocessor_path)
        
        # Load models
        for target in self.target_columns:
            for model_type in ['random_forest', 'gradient_boosting', 'logistic_regression']:
                model_key = f"{target}_{model_type}"
                model_path = os.path.join(self.models_dir, f'{prefix}_{model_key}.joblib')
                
                if os.path.exists(model_path):
                    self.models[model_key] = joblib.load(model_path)
        
        # Load metrics
        metrics_path = os.path.join(self.models_dir, f'{prefix}_metrics.json')
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                self.model_metrics = json.load(f)
        
        return len(self.models) > 0
    
    def get_model_info(self):
        """Get information about loaded models"""
        return {
            'models_loaded': list(self.models.keys()),
            'metrics': self.model_metrics,
            'preprocessor_fitted': self.preprocessor.is_fitted
        }


def train_models_from_file(dataset_path, models_dir='models', model_types=None):
    """Convenience function to train models from a dataset file"""
    trainer = HealthRiskTrainer(models_dir=models_dir)
    
    # Load dataset - support both CSV and XLSX
    try:
        if dataset_path.endswith('.xlsx') or dataset_path.endswith('.xls'):
            from .preprocessing import load_xlsx_dataset
            df = load_xlsx_dataset(dataset_path)
        else:
            df = trainer.load_dataset(dataset_path)
    except Exception as e:
        raise ValueError(f"Error loading dataset: {str(e)}")
    
    # Train models
    results = trainer.train_all_models(df, model_types)
    
    # Save models
    saved_files = trainer.save_models()
    
    return {
        'results': results,
        'saved_files': saved_files,
        'model_info': trainer.get_model_info()
    }


def train_models_from_xlsx(xlsx_path, models_dir='models'):
    """
    Train models specifically from the XLSX file
    This function loads the XLSX data, trains ML models, and saves them
    """
    from .preprocessing import load_xlsx_dataset
    
    trainer = HealthRiskTrainer(models_dir=models_dir)
    
    # Load XLSX dataset
    df = load_xlsx_dataset(xlsx_path)
    
    print(f"Loaded dataset with {len(df)} records")
    print(f"Columns: {df.columns.tolist()}")
    
    # Train models with multiple algorithms for better accuracy
    model_types = ['random_forest', 'gradient_boosting']
    results = trainer.train_all_models(df, model_types)
    
    # Save models
    saved_files = trainer.save_models()
    
    return {
        'results': results,
        'saved_files': saved_files,
        'model_info': trainer.get_model_info(),
        'dataset_info': {
            'total_records': len(df),
            'features': df.columns.tolist()
        }
    }


def get_model_performance_report(models_dir='models', prefix='health_risk'):
    """Generate a performance report for trained models"""
    trainer = HealthRiskTrainer(models_dir=models_dir)
    loaded = trainer.load_models(prefix)
    
    if not loaded:
        return {'error': 'No models found'}
    
    report = {
        'model_info': trainer.get_model_info(),
        'performance_summary': {}
    }
    
    # Summarize performance
    for model_key, metrics in trainer.model_metrics.items():
        report['performance_summary'][model_key] = {
            'accuracy': f"{metrics.get('accuracy', 0) * 100:.2f}%",
            'f1_score': f"{metrics.get('f1', 0) * 100:.2f}%",
            'cv_mean': f"{metrics.get('cv_mean', 0) * 100:.2f}%"
        }
    
    return report
