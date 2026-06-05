# ML Models package for healthcare recommendation system

from .preprocessing import (
    HealthcareDataPreprocessor,
    preprocess_health_data,
    load_xlsx_dataset,
    get_sample_dataset_info
)

from .predictor import (
    HealthRiskPredictor,
    predict_health_risks,
    get_predictor,
    get_similar_patients_recommendations,
    get_dynamic_recommendations_with_accuracy
)

from .trainer import (
    HealthRiskTrainer,
    train_models_from_file,
    train_models_from_xlsx,
    get_model_performance_report
)

__all__ = [
    'HealthcareDataPreprocessor',
    'preprocess_health_data',
    'load_xlsx_dataset',
    'get_sample_dataset_info',
    'HealthRiskPredictor',
    'predict_health_risks',
    'get_predictor',
    'get_similar_patients_recommendations',
    'get_dynamic_recommendations_with_accuracy',
    'HealthRiskTrainer',
    'train_models_from_file',
    'train_models_from_xlsx',
    'get_model_performance_report'
]
