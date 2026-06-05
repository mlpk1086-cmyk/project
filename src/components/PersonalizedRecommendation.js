import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../App.css';

//  end API URL
const API_URL = 'http://localhost:5000/api';

const PersonalizedRecommendations = () => {
  const [recommendations, setRecommendations] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [risks, setRisks] = useState(null);
  const [scores, setScores] = useState(null);
  const [detailedRecommendations, setDetailedRecommendations] = useState(null);
  const [comprehensiveRecommendations, setComprehensiveRecommendations] = useState(null);
  const [parameterRecommendations, setParameterRecommendations] = useState([]);
  const [parametersTriggered, setParametersTriggered] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedDisease, setExpandedDisease] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // overview, diet, lifestyle, actions

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      setError(null);

      try {
        // Get the JWT token from localStorage
        const token = localStorage.getItem('token');
        
        if (!token) {
          // If no token, use data from localStorage as fallback
          const localHealthData = JSON.parse(localStorage.getItem('healthData') || '{}');
          setHealthData(localHealthData);
          
          // Calculate risks locally if no backend
          const localRisks = calculateLocalRisks(localHealthData);
          setRisks(localRisks);
          setLoading(false);
          return;
        }

        // Call the backend API
        const response = await axios.get(`${API_URL}/recommendations`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        const data = response.data;
        setHealthData(data.health_data);
        setRisks(data.risks);
        setScores(data.scores);
        setRecommendations(data.recommendations);
        setDetailedRecommendations(data.detailed_recommendations);
        
        // Set comprehensive recommendations if available
        if (data.comprehensive_recommendations) {
          setComprehensiveRecommendations(data.comprehensive_recommendations);
        }
        
        // Set parameter-based recommendations (NEW)
        if (data.parameter_recommendations) {
          setParameterRecommendations(data.parameter_recommendations);
        }
        if (data.parameters_triggered) {
          setParametersTriggered(data.parameters_triggered);
        }

        // Also save to localStorage for other components
        localStorage.setItem('healthData', JSON.stringify(data.health_data));
        localStorage.setItem('risks', JSON.stringify(data.risks));
        localStorage.setItem('conditions', JSON.stringify(data.detailed_recommendations));

      } catch (err) {
        console.error('Error fetching recommendations:', err);
        
        // Fallback to localStorage data
        const localHealthData = JSON.parse(localStorage.getItem('healthData') || '{}');
        setHealthData(localHealthData);
        
        // Calculate risks locally as fallback
        const localRisks = calculateLocalRisks(localHealthData);
        setRisks(localRisks);
        
        setError('Unable to fetch recommendations from server. Showing local data.');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  // Local fallback function to calculate risks
  const calculateLocalRisks = (data) => {
    const risks = {};
    
    // Diabetes Risk
    const bmi = parseFloat(data.bmi);
    const fbs = parseFloat(data.fastingBloodSugar || data.BloodSugar || 0);
    if (bmi >= 30 || fbs >= 126) {
      risks.diabetes = 'High';
    } else if (bmi >= 25 || fbs >= 100) {
      risks.diabetes = 'Moderate';
    } else {
      risks.diabetes = 'Low';
    }

    // Anemia Risk
    const hb = parseFloat(data.hemoglobin);
    const gender = data.gender?.toLowerCase();
    const age = parseInt(data.age);
    const normalHb = gender === 'male' ? 13 : 12;
    
    if (hb < 8) {
      risks.anemia = 'High';
    } else if (hb < 11 || (gender === 'female' && age > 50)) {
      risks.anemia = 'Moderate';
    } else {
      risks.anemia = 'Low';
    }

    // Vitamin D Risk
    const vitD = parseFloat(data.vitaminD);
    const location = (data.location || '').toLowerCase();
    if (vitD < 10 || location.includes('north') || location.includes('canada')) {
      risks.vitamind = 'High';
    } else if (vitD < 20) {
      risks.vitamind = 'Moderate';
    } else {
      risks.vitamind = 'Low';
    }

    // Heart Risk
    const sys = parseInt(data.systolicBP);
    const dia = parseInt(data.diastolicBP);
    if (sys >= 140 || dia >= 90) {
      risks.heart = 'High';
    } else if (sys >= 120 || dia >= 80) {
      risks.heart = 'Moderate';
    } else {
      risks.heart = 'Low';
    }

    return risks;
  };

  // Get color class for risk level
  const getRiskColorClass = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'high':
        return 'risk-high';
      case 'moderate':
        return 'risk-moderate';
      case 'low':
        return 'risk-low';
      default:
        return '';
    }
  };

  // Get display text for risk
  const getRiskDisplayText = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'high':
        return 'High Risk';
      case 'moderate':
        return 'Moderate Risk';
      case 'low':
        return 'Low Risk';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="personal-rec-container">
      <div className="personal-rec-header">
        <div className="personal-rec-icons">
          <i className="fas fa-heart"></i>
          <i className="fas fa-stethoscope"></i>
        </div>
        <div className="personal-rec-title">Healthcare Recommendation System</div>
      </div>
      
      <div className="personal-rec-main">
        {loading && (
          <div className="ai-loading">
            <p>Loading personalized recommendations...</p>
          </div>
        )}

        {error && (
          <div className="ai-error">
            <p>{error}</p>
          </div>
        )}

        {/* Risk Summary Cards */}
        <div className="personal-rec-risks">
          <div className={`personal-rec-risk-card vitamin-d ${getRiskColorClass(risks?.vitamind)}`}>
            <h3>Vitamin D: {getRiskDisplayText(risks?.vitamind)}</h3>
            {scores?.vitamind && <p>Score: {scores.vitamind}</p>}
          </div>
          <div className={`personal-rec-risk-card diabetes ${getRiskColorClass(risks?.diabetes)}`}>
            <h3>Diabetes: {getRiskDisplayText(risks?.diabetes)}</h3>
            {scores?.diabetes && <p>Score: {scores.diabetes}</p>}
          </div>
          <div className={`personal-rec-risk-card anemia ${getRiskColorClass(risks?.anemia)}`}>
            <h3>Anemia: {getRiskDisplayText(risks?.anemia)}</h3>
            {scores?.anemia && <p>Score: {scores.anemia}</p>}
          </div>
          <div className={`personal-rec-risk-card heart ${getRiskColorClass(risks?.heart)}`}>
            <h3>Heart: {getRiskDisplayText(risks?.heart)}</h3>
            {scores?.heart && <p>Score: {scores.heart}</p>}
          </div>
        </div>

        {/* Tabs for different recommendation types */}
        <div className="rec-tabs-container">
          <div className="rec-tabs">
            <button 
              className={`rec-tab ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button 
              className={`rec-tab ${activeTab === 'diet' ? 'active' : ''}`}
              onClick={() => setActiveTab('diet')}
            >
              Diet
            </button>
            <button 
              className={`rec-tab ${activeTab === 'lifestyle' ? 'active' : ''}`}
              onClick={() => setActiveTab('lifestyle')}
            >
              Lifestyle
            </button>
            <button 
              className={`rec-tab ${activeTab === 'actions' ? 'active' : ''}`}
              onClick={() => setActiveTab('actions')}
            >
              Actions
            </button>
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="tab-content">
              <div className="personal-rec-content">
                {/* Parameter-Based Recommendations (Dynamic) */}
                {parameterRecommendations && parameterRecommendations.length > 0 && (
                  <div className="ai-recommendations parameter-recs">
                    <h2>Dynamic Parameter-Based Recommendations</h2>
                    <p className="rec-subtitle">These recommendations update automatically based on your input values</p>
                    <div className="ai-content">
                      <ul>
                        {parameterRecommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Recommendations from Backend */}
                {recommendations && recommendations.length > 0 && (
                  <div className="ai-recommendations">
                    <h2>Personalized Recommendations</h2>
                    <div className="ai-content">
                      <ul>
                        {recommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Detailed Recommendations by Condition */}
                {detailedRecommendations && (
                  <div className="personal-rec-section">
                    <h2>Detailed Recommendations</h2>
                    
                    {detailedRecommendations.diabetes && detailedRecommendations.diabetes.length > 0 && (
                      <div className="condition-recs">
                        <h3>Diabetes Recommendations</h3>
                        <ul>
                          {detailedRecommendations.diabetes.map((rec, index) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {detailedRecommendations.anemia && detailedRecommendations.anemia.length > 0 && (
                      <div className="condition-recs">
                        <h3>Anemia Recommendations</h3>
                        <ul>
                          {detailedRecommendations.anemia.map((rec, index) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {detailedRecommendations.vitamind && detailedRecommendations.vitamind.length > 0 && (
                      <div className="condition-recs">
                        <h3>Vitamin D Recommendations</h3>
                        <ul>
                          {detailedRecommendations.vitamind.map((rec, index) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {detailedRecommendations.heart && detailedRecommendations.heart.length > 0 && (
                      <div className="condition-recs">
                        <h3>Heart Health Recommendations</h3>
                        <ul>
                          {detailedRecommendations.heart.map((rec, index) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Show data if no recommendations from backend */}
                {!recommendations && !loading && risks && (
                  <div className="personal-rec-section">
                    <h2>Your Health Summary</h2>
                    <div className="health-data-display">
                      <h3>Input Data:</h3>
                      <ul>
                        <li>Age: {healthData?.age || 'N/A'}</li>
                        <li>BMI: {healthData?.bmi || 'N/A'}</li>
                        <li>Gender: {healthData?.gender || 'N/A'}</li>
                        <li>Vitamin D: {healthData?.vitaminD || 'N/A'} ng/mL</li>
                        <li>Hemoglobin: {healthData?.hemoglobin || 'N/A'} g/dL</li>
                        <li>Blood Pressure: {healthData?.systolicBP}/{healthData?.diastolicBP || 'N/A'} mmHg</li>
                        <li>Fasting Blood Sugar: {healthData?.fastingBloodSugar || 'N/A'} mg/dL</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Diet Tab */}
          {activeTab === 'diet' && (
            <div className="tab-content">
              <div className="personal-rec-section diet-section">
                <h2>Diet Recommendations</h2>
                
                {/* Diabetes Diet */}
                {comprehensiveRecommendations?.diabetes?.diet?.foods_to_eat && comprehensiveRecommendations.diabetes.diet.foods_to_eat.length > 0 && (
                  <div className="condition-recs diet-recs">
                    <h3>Diabetes - Foods to Eat</h3>
                    <ul>
                      {comprehensiveRecommendations.diabetes.diet.foods_to_eat.map((food, index) => (
                        <li key={index}>{food}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.diabetes?.diet?.foods_to_avoid && comprehensiveRecommendations.diabetes.diet.foods_to_avoid.length > 0 && (
                  <div className="condition-recs diet-recs avoid">
                    <h3>Diabetes - Foods to Avoid</h3>
                    <ul>
                      {comprehensiveRecommendations.diabetes.diet.foods_to_avoid.map((food, index) => (
                        <li key={index}>{food}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Vitamin D Diet */}
                {comprehensiveRecommendations?.vitamind?.diet?.foods_to_eat && comprehensiveRecommendations.vitamind.diet.foods_to_eat.length > 0 && (
                  <div className="condition-recs diet-recs">
                    <h3>Vitamin D - Foods to Eat</h3>
                    <ul>
                      {comprehensiveRecommendations.vitamind.diet.foods_to_eat.map((food, index) => (
                        <li key={index}>{food}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.vitamind?.diet?.foods_to_avoid && comprehensiveRecommendations.vitamind.diet.foods_to_avoid.length > 0 && (
                  <div className="condition-recs diet-recs avoid">
                    <h3>Vitamin D - Foods to Avoid</h3>
                    <ul>
                      {comprehensiveRecommendations.vitamind.diet.foods_to_avoid.map((food, index) => (
                        <li key={index}>{food}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Anemia Diet */}
                {comprehensiveRecommendations?.anemia?.diet?.foods_to_eat && comprehensiveRecommendations.anemia.diet.foods_to_eat.length > 0 && (
                  <div className="condition-recs diet-recs">
                    <h3>Anemia - Foods to Eat</h3>
                    <ul>
                      {comprehensiveRecommendations.anemia.diet.foods_to_eat.map((food, index) => (
                        <li key={index}>{food}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.anemia?.diet?.foods_to_avoid && comprehensiveRecommendations.anemia.diet.foods_to_avoid.length > 0 && (
                  <div className="condition-recs diet-recs avoid">
                    <h3>Anemia - Foods to Avoid</h3>
                    <ul>
                      {comprehensiveRecommendations.anemia.diet.foods_to_avoid.map((food, index) => (
                        <li key={index}>{food}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Heart Diet */}
                {comprehensiveRecommendations?.heart?.diet?.foods_to_eat && comprehensiveRecommendations.heart.diet.foods_to_eat.length > 0 && (
                  <div className="condition-recs diet-recs">
                    <h3>Heart Health - Foods to Eat</h3>
                    <ul>
                      {comprehensiveRecommendations.heart.diet.foods_to_eat.map((food, index) => (
                        <li key={index}>{food}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.heart?.diet?.foods_to_avoid && comprehensiveRecommendations.heart.diet.foods_to_avoid.length > 0 && (
                  <div className="condition-recs diet-recs avoid">
                    <h3>Heart Health - Foods to Avoid</h3>
                    <ul>
                      {comprehensiveRecommendations.heart.diet.foods_to_avoid.map((food, index) => (
                        <li key={index}>{food}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* General Diet Recommendations */}
                {!comprehensiveRecommendations && (
                  <p className="no-recs">No diet recommendations available. Please complete your health assessment.</p>
                )}
              </div>
            </div>
          )}

          {/* Lifestyle Tab */}
          {activeTab === 'lifestyle' && (
            <div className="tab-content">
              <div className="personal-rec-section lifestyle-section">
                <h2>Lifestyle Recommendations</h2>
                
                {/* Diabetes Lifestyle */}
                {comprehensiveRecommendations?.diabetes?.lifestyle?.exercise && comprehensiveRecommendations.diabetes.lifestyle.exercise.length > 0 && (
                  <div className="condition-recs lifestyle-recs">
                    <h3>Diabetes - Exercise</h3>
                    <ul>
                      {comprehensiveRecommendations.diabetes.lifestyle.exercise.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.diabetes?.lifestyle?.sleep && comprehensiveRecommendations.diabetes.lifestyle.sleep.length > 0 && (
                  <div className="condition-recs lifestyle-recs">
                    <h3>Diabetes - Sleep</h3>
                    <ul>
                      {comprehensiveRecommendations.diabetes.lifestyle.sleep.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Vitamin D Lifestyle */}
                {comprehensiveRecommendations?.vitamind?.lifestyle?.exercise && comprehensiveRecommendations.vitamind.lifestyle.exercise.length > 0 && (
                  <div className="condition-recs lifestyle-recs">
                    <h3>Vitamin D - Exercise & Sun Exposure</h3>
                    <ul>
                      {comprehensiveRecommendations.vitamind.lifestyle.exercise.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Anemia Lifestyle */}
                {comprehensiveRecommendations?.anemia?.lifestyle?.habits && comprehensiveRecommendations.anemia.lifestyle.habits.length > 0 && (
                  <div className="condition-recs lifestyle-recs">
                    <h3>Anemia - Healthy Habits</h3>
                    <ul>
                      {comprehensiveRecommendations.anemia.lifestyle.habits.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Heart Lifestyle */}
                {comprehensiveRecommendations?.heart?.lifestyle?.exercise && comprehensiveRecommendations.heart.lifestyle.exercise.length > 0 && (
                  <div className="condition-recs lifestyle-recs">
                    <h3>Heart - Exercise</h3>
                    <ul>
                      {comprehensiveRecommendations.heart.lifestyle.exercise.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.heart?.lifestyle?.stress_management && comprehensiveRecommendations.heart.lifestyle.stress_management.length > 0 && (
                  <div className="condition-recs lifestyle-recs">
                    <h3>Heart - Stress Management</h3>
                    <ul>
                      {comprehensiveRecommendations.heart.lifestyle.stress_management.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {!comprehensiveRecommendations && (
                  <p className="no-recs">No lifestyle recommendations available. Please complete your health assessment.</p>
                )}
              </div>
            </div>
          )}

          {/* Actions Tab */}
          {activeTab === 'actions' && (
            <div className="tab-content">
              <div className="personal-rec-section actions-section">
                <h2>Actionable Steps</h2>
                
                {/* Diabetes Actions */}
                {comprehensiveRecommendations?.diabetes?.actions?.immediate_actions && comprehensiveRecommendations.diabetes.actions.immediate_actions.length > 0 && (
                  <div className="condition-recs actions-recs">
                    <h3>Diabetes - Immediate Actions</h3>
                    <ul>
                      {comprehensiveRecommendations.diabetes.actions.immediate_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.diabetes?.actions?.short_term_actions && comprehensiveRecommendations.diabetes.actions.short_term_actions.length > 0 && (
                  <div className="condition-recs actions-recs">
                    <h3>Diabetes - Short Term Actions</h3>
                    <ul>
                      {comprehensiveRecommendations.diabetes.actions.short_term_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.diabetes?.actions?.recommended_tests && comprehensiveRecommendations.diabetes.actions.recommended_tests.length > 0 && (
                  <div className="condition-recs actions-recs tests">
                    <h3>Diabetes - Recommended Tests</h3>
                    <ul>
                      {comprehensiveRecommendations.diabetes.actions.recommended_tests.map((test, index) => (
                        <li key={index}>{test}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Vitamin D Actions */}
                {comprehensiveRecommendations?.vitamind?.actions?.immediate_actions && comprehensiveRecommendations.vitamind.actions.immediate_actions.length > 0 && (
                  <div className="condition-recs actions-recs">
                    <h3>Vitamin D - Immediate Actions</h3>
                    <ul>
                      {comprehensiveRecommendations.vitamind.actions.immediate_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Anemia Actions */}
                {comprehensiveRecommendations?.anemia?.actions?.immediate_actions && comprehensiveRecommendations.anemia.actions.immediate_actions.length > 0 && (
                  <div className="condition-recs actions-recs">
                    <h3>Anemia - Immediate Actions</h3>
                    <ul>
                      {comprehensiveRecommendations.anemia.actions.immediate_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.anemia?.actions?.recommended_tests && comprehensiveRecommendations.anemia.actions.recommended_tests.length > 0 && (
                  <div className="condition-recs actions-recs tests">
                    <h3>Anemia - Recommended Tests</h3>
                    <ul>
                      {comprehensiveRecommendations.anemia.actions.recommended_tests.map((test, index) => (
                        <li key={index}>{test}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Heart Actions */}
                {comprehensiveRecommendations?.heart?.actions?.immediate_actions && comprehensiveRecommendations.heart.actions.immediate_actions.length > 0 && (
                  <div className="condition-recs actions-recs">
                    <h3>Heart - Immediate Actions</h3>
                    <ul>
                      {comprehensiveRecommendations.heart.actions.immediate_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {comprehensiveRecommendations?.heart?.actions?.recommended_tests && comprehensiveRecommendations.heart.actions.recommended_tests.length > 0 && (
                  <div className="condition-recs actions-recs tests">
                    <h3>Heart - Recommended Tests</h3>
                    <ul>
                      {comprehensiveRecommendations.heart.actions.recommended_tests.map((test, index) => (
                        <li key={index}>{test}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {!comprehensiveRecommendations && (
                  <p className="no-recs">No actionable steps available. Please complete your health assessment.</p>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="personal-rec-download-btn">
          <Link to="/report" className="report-btn">View Health Report</Link>
          <button className="generate-report-btn" onClick={() => localStorage.setItem('generateReport', 'true')}>
            Generate Comprehensive Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default PersonalizedRecommendations;

