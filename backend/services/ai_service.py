"""
AI Service
Handles AI-powered health recommendations using Google Gemini API
"""

from typing import Optional, Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service for generating AI-powered recommendations"""
    
    def __init__(self, api_key: str, model: str = 'gemini-2.0-flash', 
                 temperature: float = 0.7, max_tokens: int = 2048):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta/models'
    
    def generate_recommendations(self, health_data: Dict[str, Any], 
                                  risks: Dict[str, str], 
                                  scores: Dict[str, int]) -> Optional[str]:
        """
        Generate personalized AI recommendations based on health data and risks
        
        Args:
            health_data: Dictionary containing patient's health metrics
            risks: Dictionary of risk levels for each condition
            scores: Dictionary of risk scores for each condition
            
        Returns:
            AI-generated recommendations or None if failed
        """
        prompt = self._build_prompt(health_data, risks, scores)
        
        try:
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens
                }
            }
            
            response = requests.post(
                url, 
                json=payload, 
                headers={'Content-Type': 'application/json'}, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    return data['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.error(f'AI API error: {response.status_code} - {response.text}')
                
        except requests.exceptions.Timeout:
            logger.error('AI API timeout')
        except requests.exceptions.RequestException as e:
            logger.error(f'AI API request failed: {str(e)}')
        except Exception as e:
            logger.error(f'Error generating AI recommendations: {str(e)}')
        
        return None
    
    def _build_prompt(self, health_data: Dict[str, Any], 
                      risks: Dict[str, str], 
                      scores: Dict[str, int]) -> str:
        """Build prompt for AI model"""
        prompt = f"""You are a healthcare AI assistant. Based on the following patient health data and risk assessment, provide personalized health recommendations.

Patient Health Data:
- Age: {health_data.get('age', 'Not provided')}
- Gender: {health_data.get('gender', 'Not provided')}
- BMI: {health_data.get('bmi', 'Not provided')}
- Smoking Status: {health_data.get('smokingStatus', 'Not provided')}
- Location: {health_data.get('location', 'Not provided')}
- Blood Pressure: {health_data.get('systolicBP', 'N/A')}/{health_data.get('diastolicBP', 'N/A')} mmHg
- Fasting Blood Sugar: {health_data.get('fastingBloodSugar', 'Not provided')} mg/dL
- Hemoglobin: {health_data.get('hemoglobin', 'Not provided')} g/dL
- Vitamin D: {health_data.get('vitaminD', 'Not provided')} ng/mL
- Total Cholesterol: {health_data.get('totalCholesterol', 'Not provided')} mg/dL
- HDL Cholesterol: {health_data.get('hdlCholesterol', 'Not provided')} mg/dL
- Physical Activity: {health_data.get('physicalActivity', 'Not provided')}

Risk Assessment:
- Diabetes Risk: {risks.get('diabetes', 'Unknown')} (Score: {scores.get('diabetes', 0)})
- Anemia Risk: {risks.get('anemia', 'Unknown')} (Score: {scores.get('anemia', 0)})
- Vitamin D Risk: {risks.get('vitamind', 'Unknown')} (Score: {scores.get('vitamind', 0)})
- Heart Risk: {risks.get('heart', 'Unknown')} (Score: {scores.get('heart', 0)})

Please provide:
1. A brief summary of the patient's health status
2. Specific actionable recommendations for each risk area
3. Lifestyle modifications suggested
4. When to seek medical attention

Format your response as a clear, numbered list with sections."""
        
        return prompt


# Singleton instance - will be initialized with config
_ai_service = None


def get_ai_service(api_key: str = None, model: str = 'gemini-2.0-flash',
                   temperature: float = 0.7, max_tokens: int = 2048) -> Optional[AIService]:
    """
    Get or create AI service instance
    
    Args:
        api_key: Google AI API key (will use env var if not provided)
        model: AI model name
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        
    Returns:
        AIService instance or None if no API key
    """
    global _ai_service
    
    if api_key is None:
        import os
        api_key = os.getenv('GOOGLE_AI_API_KEY', '')
    
    if not api_key:
        logger.warning('No Google AI API key provided')
        return None
    
    if _ai_service is None:
        _ai_service = AIService(api_key, model, temperature, max_tokens)
    
    return _ai_service

