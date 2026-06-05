import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../App.css';

const Dashboard = () => {
  const [expandedSections, setExpandedSections] = useState({
    vitaminD: false,
    diabetes: false,
    anemia: false,
    heart: false
  });

  const [formData, setFormData] = useState({
    age: '', gender: '', bmi: '', smokingStatus: '',
    location: '', height: '', weight: '', physicalActivity: ''  
  });

  const [vitaminDData, setVitaminDData] = useState({
    location: '', smokingStatus: '', dietType: '', sunExposure: '',
    vitaminDPercentRda: '', calciumPercentRda: '', ironPercentRda: '',
    serumVitaminDNgml: '', alcoholConsumption: '', exerciseLevel: '',
    hemoglobinGdl: ''
  });

  const [diabetesData, setDiabetesData] = useState({
    fastingBloodSugar: '', hbA1cLevel: '', systolicBP: '',
    diastolicBP: '', totalCholesterol: '', hdlCholesterol: '', 
    age: '', gender: '', height: '', weight: '',
    location: 'India', familyHistoryDiabetes: ''
  });






const [anemiaData, setAnemiaData] = useState({
    hemoglobinGdl: '', ironIntake: '', vitaminB12Level: '', diet: '', location: '', fatigueSymptoms: ''
  });

  const [heartData, setHeartData] = useState({
    systolicBP: '', diastolicBP: '', totalCholesterol: '',
    hdlCholesterol: '', ldlCholesterol: '', triglycerides: '',
    heartRate: '', fastingBloodSugar: '', ecg: ''
  });


  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dynamicRecommendations, setDynamicRecommendations] = useState([]);
  const [showDynamicRecs, setShowDynamicRecs] = useState(false);

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
    setRecommendations(null);
    setDynamicRecommendations([]);
  };

  const handleCommonChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const updatedData = { ...prev, [name]: value };
      if (name === 'height' || name === 'weight') {
        const height = parseFloat(name === 'height' ? value : prev.height);
        const weight = parseFloat(name === 'weight' ? value : prev.weight);
        if (!isNaN(height) && !isNaN(weight) && height > 0) {
          updatedData.bmi = (weight / Math.pow(height / 100, 2)).toFixed(1);
        }
      }
      return updatedData;
    });
  };

const handleDiabetesChange = (e) => {
    const { name, value } = e.target;
    
    // Sync height/weight to formData for BMI calculation
    if (name === 'height' || name === 'weight') {
      setFormData(prev => {
        const updatedData = { ...prev, [name]: value };
        const height = parseFloat(name === 'height' ? value : prev.height);
        const weight = parseFloat(name === 'weight' ? value : prev.weight);
        if (!isNaN(height) && !isNaN(weight) && height > 0) {
          updatedData.bmi = (weight / Math.pow(height / 100, 2)).toFixed(1);
        }
        return updatedData;
      });
    }
    
    setDiabetesData(prev => ({ ...prev, [name]: value }));
    setTimeout(() => updateDynamicRecommendations('diabetes'), 100);
  };

  const handleDiabetesCommonChange = (e) => {
    const { name, value } = e.target;
    handleCommonChange(e); // Update formData + BMI
    setDiabetesData(prev => ({ ...prev, [name]: value }));
  };


  const handleVitaminDChange = (e) => {
    const { name, value } = e.target;
    setVitaminDData(prev => ({ ...prev, [name]: value }));
    setTimeout(() => updateDynamicRecommendations('vitaminD'), 100);
  };

  const [diabetesApiData, setDiabetesApiData] = useState(null);



  const handleAnemiaChange = (e) => {
    const { name, value } = e.target;
    setAnemiaData(prev => ({ ...prev, [name]: value }));
    setTimeout(() => updateDynamicRecommendations('anemia'), 100);
  };

  const handleHeartChange = (e) => {
    const { name, value } = e.target;
    setHeartData(prev => ({ ...prev, [name]: value }));
    setTimeout(() => updateDynamicRecommendations('heart'), 100);
  };

  // Dynamic recommendations for Vitamin D
  const getVitaminDParameterRecs = () => {
    const recs = [];
    const vd = vitaminDData;
    const common = formData;
    const serumVitaminD = parseFloat(vd.serumVitaminDNgml);
    
    if (!isNaN(serumVitaminD)) {
      if (serumVitaminD < 10) {
        recs.push('SEVERE Vitamin D Deficiency (< 10 ng/mL) - Consult doctor immediately');
        recs.push('Consider Vitamin D3 4000-10000 IU daily under medical supervision');
      } else if (serumVitaminD < 20) {
        recs.push('Vitamin D Insufficiency detected (10-20 ng/mL)');
        recs.push('Consider Vitamin D3 2000-4000 IU daily');
      } else if (serumVitaminD < 30) {
        recs.push('Vitamin D is insufficient (20-30 ng/mL)');
      } else if (serumVitaminD >= 30 && serumVitaminD <= 100) {
        recs.push('Vitamin D levels are normal');
      }
    }
    
    const sunExp = parseFloat(vd.sunExposure);
    if (!isNaN(sunExp) && sunExp < 0.5) {
      recs.push('Limited sun exposure - consider supplements');
    }
    
    const bmi = parseFloat(common.bmi);
    if (!isNaN(bmi) && bmi >= 30) {
      recs.push('Obesity affects Vitamin D metabolism');
    }
    
    const age = parseInt(common.age);
    if (!isNaN(age) && age > 65) {
      recs.push('Age > 65: Vitamin D production decreases');
    }
    
    if (vd.alcoholConsumption === 'heavy') {
      recs.push('Heavy alcohol affects Vitamin D');
    }
    
    if (vd.exerciseLevel === 'none') {
      recs.push('No exercise - try outdoor activities');
    }
    
    return recs;
  };

  // Dynamic recommendations for Diabetes
  const getDiabetesParameterRecs = () => {
    const recs = [];
    const db = diabetesData;
    const common = formData;
    const fbs = parseFloat(db.fastingBloodSugar);
    
    if (!isNaN(fbs)) {
      if (fbs >= 126) {
        recs.push('CRITICAL: Blood sugar >= 126 mg/dL indicates diabetes');
        recs.push('Consult endocrinologist immediately');
      } else if (fbs >= 100) {
        recs.push('Prediabetes detected (100-125 mg/dL)');
        recs.push('Reduce sugar, increase exercise');
      } else if (fbs >= 70 && fbs < 100) {
        recs.push('Blood sugar is normal');
      }
    }
    
    const hba1c = parseFloat(db.hbA1cLevel);
    if (!isNaN(hba1c) && hba1c >= 6.5) {
      recs.push('HbA1c >= 6.5% indicates diabetes');
    }
    
    const bmi = parseFloat(common.bmi);
    if (!isNaN(bmi) && bmi >= 35) {
      recs.push('BMI >= 35 significantly increases diabetes risk');
    } else if (!isNaN(bmi) && bmi >= 30) {
      recs.push('Obesity increases diabetes risk');
    }
    
    if (common.physicalActivity === 'sedentary' || common.physicalActivity === '') {
      recs.push('Sedentary lifestyle is a major risk factor');
    }
    
    if (common.smokingStatus === 'yes') {
      recs.push('Smoking increases diabetes complications');
    }
    
    return recs;
  };

  // Dynamic recommendations for Anemia
  const getAnemiaParameterRecs = () => {
    const recs = [];
    const ad = anemiaData;
    const common = formData;
    const hemoglobin = parseFloat(ad.hemoglobinGdl);
    
    if (!isNaN(hemoglobin)) {
      if (hemoglobin < 8) {
        recs.push('⚠️ SEVERE Anemia detected (Hemoglobin < 8 g/dL) - Consult hematologist immediately');
        recs.push('Consider iron infusion therapy');
        recs.push('Test for underlying causes (GI bleeding, bone marrow disorders)');
      } else if (hemoglobin < 10) {
        recs.push('⚠️ Moderate to Severe Anemia (Hemoglobin 8-10 g/dL)');
        recs.push('Schedule appointment with healthcare provider');
        recs.push('Increase iron-rich foods: red meat, beans, leafy greens');
      } else if (hemoglobin < 12) {
        recs.push('⚠️ Mild Anemia detected (Hemoglobin 10-12 g/dL)');
        recs.push('Increase dietary iron intake');
        recs.push('Eat iron-rich foods with vitamin C for better absorption');
      }
    }
    
    if (ad.ironIntake === 'low') {
      recs.push('⚠️ Low iron intake detected');
      recs.push('Increase iron-rich foods: red meat, poultry, fish, beans, spinach');
      if (ad.diet === 'vegetarian') {
        recs.push('Vegetarian: Focus on plant iron + Vitamin C (spinach + lemon)');
      }
    }

    const b12 = parseFloat(ad.vitaminB12Level);
    if (!isNaN(b12) && b12 < 200) {
      recs.push('⚠️ LOW Vitamin B12 detected - Consider B12 supplements/injections');
      if (ad.diet === 'vegetarian' || ad.diet === 'vegan') {
        recs.push('Vegetarian/Vegan: B12 supplementation essential');
      }
    }

    if (ad.fatigueSymptoms === 'severe') {
      recs.push('⚠️ Severe fatigue - Important anemia symptom, seek medical evaluation');
    } else if (ad.fatigueSymptoms === 'moderate') {
      recs.push('Moderate fatigue noted - Monitor and improve nutrition');
    }
    
    if (common.gender === 'female') {
      recs.push('📊 Female: Higher risk for iron deficiency due to menstruation');
    }
    
    return recs;
  };

  // Dynamic recommendations for Heart
  const getHeartParameterRecs = () => {
    const recs = [];
    const hd = heartData;
    const common = formData;
    
    const systolic = parseFloat(hd.systolicBP);
    if (!isNaN(systolic)) {
      if (systolic >= 180) {
        recs.push('⚠️ CRITICAL: Hypertensive Crisis (Systolic BP ≥ 180 mmHg) - Seek immediate medical attention');
      } else if (systolic >= 140) {
        recs.push('⚠️ High Blood Pressure (Stage 2: ≥ 140 mmHg)');
        recs.push('Reduce sodium intake to < 1500 mg/day');
      } else if (systolic >= 130) {
        recs.push('⚠️ High Blood Pressure (Stage 1: 130-139 mmHg)');
        recs.push('Consider lifestyle modifications');
      }
    }
    
    const diastolic = parseFloat(hd.diastolicBP);
    if (!isNaN(diastolic) && diastolic >= 90) {
      recs.push('⚠️ High Diastolic BP (≥ 90 mmHg)');
    }
    
    const totalChol = parseFloat(hd.totalCholesterol);
    if (!isNaN(totalChol)) {
      if (totalChol >= 240) {
        recs.push('⚠️ High Cholesterol (≥ 240 mg/dL) - Discuss with healthcare provider');
      } else if (totalChol >= 200) {
        recs.push('⚠️ Borderline High Cholesterol (200-239 mg/dL)');
      }
    }
    
    const hdl = parseFloat(hd.hdlCholesterol);
    if (!isNaN(hdl) && hdl < 40) {
      recs.push('⚠️ Low HDL Cholesterol (< 40 mg/dL) - Increase aerobic exercise');
    }
    
    if (common.smokingStatus === 'yes') {
      recs.push('⚠️ SMOKING is a major cardiovascular risk factor - Quit smoking');
    }
    
    if (common.physicalActivity === 'sedentary' || common.physicalActivity === 'none' || common.physicalActivity === '') {
      recs.push('⚠️ Sedentary lifestyle increases heart disease risk');
    }
    
    return recs;
  };

  const updateDynamicRecommendations = (section) => {
    const allRecs = [];
    if (section === 'vitaminD' || (expandedSections.vitaminD && !section)) {
      allRecs.push(...getVitaminDParameterRecs());
    }
    if (section === 'diabetes' || (expandedSections.diabetes && !section)) {
      allRecs.push(...getDiabetesParameterRecs());
    }
    if (section === 'anemia' || (expandedSections.anemia && !section)) {
      allRecs.push(...getAnemiaParameterRecs());
    }
    if (section === 'heart' || (expandedSections.heart && !section)) {
      allRecs.push(...getHeartParameterRecs());
    }
    const uniqueRecs = [...new Set(allRecs)];
    setDynamicRecommendations(uniqueRecs);
    if (uniqueRecs.length > 0) setShowDynamicRecs(true);
  };

  const calculateVitaminDRisk = () => {
    let riskScore = 0;
    const factors = [];
    const vd = vitaminDData;
    const common = formData;

    const serumVitaminD = parseFloat(vd.serumVitaminDNgml);
    if (!isNaN(serumVitaminD)) {
      if (serumVitaminD < 10) { riskScore += 5; factors.push({ factor: 'Severely low Vitamin D', severity: 'high' }); }
      else if (serumVitaminD < 20) { riskScore += 4; factors.push({ factor: 'Low Vitamin D', severity: 'high' }); }
      else if (serumVitaminD < 30) { riskScore += 2; factors.push({ factor: 'Insufficient Vitamin D', severity: 'moderate' }); }
    }

    const bmi = parseFloat(common.bmi);
    if (!isNaN(bmi) && bmi >= 30) { riskScore += 2; factors.push({ factor: 'Obesity', severity: 'moderate' }); }

    const age = parseInt(common.age);
    if (!isNaN(age) && age > 65) { riskScore += 2; factors.push({ factor: 'Age > 65', severity: 'moderate' }); }

    if (vd.alcoholConsumption === 'heavy') { riskScore += 3; factors.push({ factor: 'Heavy alcohol', severity: 'high' }); }
    if (vd.exerciseLevel === 'none') { riskScore += 2; factors.push({ factor: 'No exercise', severity: 'moderate' }); }

    let riskLevel = riskScore >= 6 ? 'High' : riskScore >= 3 ? 'Moderate' : 'Low';
    let riskCategory = riskScore >= 6 ? 'deficiency' : riskScore >= 3 ? 'insufficiency' : 'normal';
    return { riskLevel, riskCategory, riskScore, factors };
  };

  const calculateDiabetesRisk = () => {
    let riskScore = 0;
    const factors = [];
    const db = diabetesData;
    const common = formData;

    const fbs = parseFloat(db.fastingBloodSugar);
    if (!isNaN(fbs)) {
      if (fbs >= 126) { riskScore += 5; factors.push({ factor: 'Diabetes range blood sugar', severity: 'high' }); }
      else if (fbs >= 100) { riskScore += 3; factors.push({ factor: 'Prediabetes blood sugar', severity: 'moderate' }); }
    }

    const bmi = parseFloat(common.bmi);
    if (!isNaN(bmi)) {
      if (bmi >= 30) { riskScore += 3; factors.push({ factor: 'Obesity', severity: 'high' }); }
      else if (bmi >= 25) { riskScore += 2; factors.push({ factor: 'Overweight', severity: 'moderate' }); }
    }

    const age = parseInt(common.age);
    if (!isNaN(age) && age > 45) { riskScore += 2; factors.push({ factor: 'Age > 45', severity: 'moderate' }); }

    if (common.physicalActivity === 'sedentary' || common.physicalActivity === '') {
      riskScore += 2; factors.push({ factor: 'Sedentary lifestyle', severity: 'moderate' });
    }

    let riskLevel = riskScore >= 8 ? 'High' : riskScore >= 4 ? 'Moderate' : 'Low';
    return { riskLevel, riskCategory: riskLevel.toLowerCase(), riskScore, factors };
  };

  const calculateAnemiaRisk = () => {
    let riskScore = 0;
    const factors = [];
    const ad = anemiaData;
    const common = formData;

    const hemoglobin = parseFloat(ad.hemoglobinGdl);
    if (!isNaN(hemoglobin)) {
      if (common.gender === 'female') {
        if (hemoglobin < 12) { riskScore += 5; factors.push({ factor: 'Low Hemoglobin (Female)', severity: 'high' }); }
      } else {
        if (hemoglobin < 13.5) { riskScore += 5; factors.push({ factor: 'Low Hemoglobin (Male)', severity: 'high' }); }
      }
    }

    if (ad.ironIntake === 'low') { riskScore += 3; factors.push({ factor: 'Low iron intake', severity: 'high' }); }

    const b12 = parseFloat(ad.vitaminB12Level);
    if (!isNaN(b12) && b12 < 200) { 
      riskScore += 4; 
      factors.push({ factor: 'Vitamin B12 deficiency', severity: 'high' }); 
    }

    if (ad.diet === 'vegetarian' || ad.diet === 'vegan') { 
      riskScore += 2; 
      factors.push({ factor: 'Vegetarian/Vegan diet (B12 risk)', severity: 'moderate' }); 
    }

    if (ad.fatigueSymptoms === 'moderate' || ad.fatigueSymptoms === 'severe') { 
      riskScore += 2; 
      factors.push({ factor: 'Significant fatigue symptoms', severity: 'moderate' }); 
    }

    let riskLevel = riskScore >= 10 ? 'High' : riskScore >= 5 ? 'Moderate' : 'Low';
    return { riskLevel, riskCategory: riskLevel.toLowerCase(), riskScore, factors };
  };

  const calculateHeartRisk = () => {
    let riskScore = 0;
    const factors = [];
    const hd = heartData;
    const common = formData;

    const systolic = parseFloat(hd.systolicBP);
    if (!isNaN(systolic) && systolic >= 140) { riskScore += 4; factors.push({ factor: 'High blood pressure', severity: 'high' }); }

    const totalChol = parseFloat(hd.totalCholesterol);
    if (!isNaN(totalChol) && totalChol >= 240) { riskScore += 3; factors.push({ factor: 'High cholesterol', severity: 'high' }); }

    if (common.smokingStatus === 'yes') { riskScore += 3; factors.push({ factor: 'Smoking', severity: 'high' }); }

    let riskLevel = riskScore >= 8 ? 'High' : riskScore >= 4 ? 'Moderate' : 'Low';
    return { riskLevel, riskCategory: riskLevel.toLowerCase(), riskScore, factors };
  };

  const getVitaminDRecommendations = (riskCategory) => {
    if (riskCategory === 'deficiency') {
      return [
        {
          title: 'High Risk - Vitamin D Deficiency',
          riskLevel: 'High',
          riskFactors: [
            'Severely low serum Vitamin D level (< 10 ng/mL)',
            'High risk of bone demineralization',
            'Potential immune system impairment',
            'Increased risk of fractures'
          ],
          recommendedActions: [
            '⚠️ Consult doctor immediately for high-dose supplementation',
            'Take Vitamin D3 4000-10000 IU daily under medical supervision',
            'Increase sun exposure 30-60 minutes daily (midday)',
            'Re-test Vitamin D levels in 3 months',
            'Test calcium, phosphorus, and PTH levels'
          ],
          dietRecommendations: {
            foodsToEat: [
              'Fatty fish (salmon, mackerel, sardines) - 2-3 times per week',
              'Cod liver oil (1 tablespoon daily)',
              'Egg yolks (2-4 daily)',
              'Fortified dairy products (milk, yogurt, cheese)',
              'Fortified plant-based milks (soy, almond, oat)',
              'Mushrooms (UV-exposed)',
              'Beef liver (once a week)'
            ],
            foodsToAvoid: [
              'Highly processed foods low in nutrients',
              'Excessive caffeine (can affect calcium absorption)',
              'Soft drinks (displace nutrient-rich beverages)'
            ]
          },
          lifestyleRecommendations: [
            'Get safe sun exposure (30-60 minutes midday)',
            'Include outdoor exercise (walking, jogging)',
            'Maintain regular sleep schedule (7-9 hours)',
            'Manage stress through meditation or yoga'
          ],
          additionalSupport: [
            'Calcium supplementation (1000-1200 mg daily)',
            'Consider magnesium supplementation',
            'Vitamin K2 for bone health',
            'Regular bone density monitoring (DEXA scan)'
          ]
        }
      ];
    } else if (riskCategory === 'insufficiency') {
      return [
        {
          title: 'Moderate Risk - Vitamin D Insufficiency',
          riskLevel: 'Moderate',
          riskFactors: [
            'Insufficient serum Vitamin D level (10-20 ng/mL)',
            'Reduced calcium absorption',
            'Potential bone health impact',
            'May affect immune function'
          ],
          recommendedActions: [
            'Consider Vitamin D3 supplementation (2000-4000 IU daily)',
            'Increase sun exposure to 20-30 minutes daily',
            'Add more Vitamin D-rich foods to diet',
            'Re-test Vitamin D levels in 3-6 months',
            'Discuss supplementation with healthcare provider'
          ],
          dietRecommendations: {
            foodsToEat: [
              'Fatty fish (salmon, mackerel, tuna) - 2 times per week',
              'Egg yolks (1-2 daily)',
              'Fortified dairy products',
              'Fortified cereals',
              'Mushrooms (UV-exposed)'
            ],
            foodsToAvoid: [
              'Processed foods',
              'Excessive caffeine with meals'
            ]
          },
          lifestyleRecommendations: [
            'Get moderate sun exposure (15-20 minutes daily)',
            'Include weight-bearing exercises',
            'Maintain adequate sleep',
            'Consider outdoor activities'
          ],
          additionalSupport: [
            'Calcium supplementation (500-1000 mg daily)',
            'Consider vitamin D3 supplements',
            'Regular monitoring of levels'
          ]
        }
      ];
    }
    return [
      {
        title: 'Low Risk - Normal Vitamin D',
        riskLevel: 'Low',
        riskFactors: [],
        recommendedActions: [
          'Maintain current Vitamin D levels through balanced diet',
          'Continue regular sun exposure (10-15 minutes daily)',
          'Include Vitamin D-rich foods in diet',
          'Consider annual Vitamin D testing if at risk'
        ],
        dietRecommendations: {
          foodsToEat: [
            'Fatty fish (salmon, mackerel)',
            'Egg yolks',
            'Fortified dairy products',
            'Varied diet with nutrients'
          ],
          foodsToAvoid: []
        },
        lifestyleRecommendations: [
          'Maintain adequate sun exposure',
          'Regular physical activity',
          'Balanced diet rich in nutrients'
        ],
        additionalSupport: [
          'Annual Vitamin D screening if at risk',
          'Continue current lifestyle'
        ]
      }
    ];
  };

  const getDiabetesRecommendations = (riskCategory) => {
    if (riskCategory === 'high') {
      return [
        {
          title: 'High Risk - Diabetes',
          riskLevel: 'High',
          riskFactors: [
            '⚠️ Blood sugar in diabetes range (≥ 126 mg/dL fasting)',
            '⚠️ High HbA1c level (≥ 6.5%)',
            'Obesity (BMI ≥ 30) significantly increases insulin resistance',
            'Advanced age (> 45) increases diabetes risk',
            'Sedentary lifestyle contributes to insulin resistance',
            'Family history of diabetes may be present'
          ],
          recommendedActions: [
            '⚠️ Consult endocrinologist immediately',
            'Schedule fasting blood sugar and HbA1c tests',
            'Begin blood glucose monitoring immediately',
            'Start low-carbohydrate diet under medical supervision',
            'Consider diabetes medication if prescribed by doctor',
            'Schedule eye examination for diabetic retinopathy screening',
            'Get foot examination and podiatrist consultation'
          ],
          dietRecommendations: {
            foodsToEat: [
              'Leafy green vegetables (spinach, kale, broccoli)',
              'Non-starchy vegetables (bell peppers, cucumbers, tomatoes)',
              'Whole grains (brown rice, quinoa, oats)',
              'Lean proteins (chicken, fish, turkey, tofu)',
              'Healthy fats (avocado, olive oil, nuts)',
              'Berries (blueberries, strawberries)',
              'Legumes (beans, lentils, chickpeas)',
              'Greek yogurt (unsweetened)'
            ],
            foodsToAvoid: [
              'Sugary drinks (soda, fruit juices)',
              'Refined carbohydrates (white bread, white rice)',
              'Processed foods (chips, cookies)',
              'Fried foods (french fries)',
              'Trans fats (margarine)',
              'High-sodium foods (canned soups)'
            ]
          },
          lifestyleRecommendations: [
            'Aim for 150+ minutes of moderate exercise per week',
            'Include strength training 2-3 times per week',
            'Walk 10-15 minutes after each meal',
            'Get 7-9 hours of quality sleep nightly',
            'Practice stress management (meditation, deep breathing)',
            'Monitor blood sugar levels regularly as recommended',
            'Quit smoking if currently smoking'
          ],
          additionalSupport: [
            'Enroll in diabetes education program',
            'Work with registered dietitian for meal planning',
            'Consider continuous glucose monitoring (CGM)',
            'Regular follow-up with healthcare provider (monthly)',
            'Annual comprehensive diabetes screening',
            'Kidney function tests (Creatinine, eGFR) yearly',
            'Foot care and regular podiatrist visits'
          ]
        }
      ];
    } else if (riskCategory === 'moderate') {
      return [
        {
          title: 'Moderate Risk - Prediabetes',
          riskLevel: 'Moderate',
          riskFactors: [
            'Prediabetes blood sugar level (100-125 mg/dL)',
            'Overweight (BMI 25-29.9)',
            'Age > 45 increases risk',
            'Sedentary lifestyle',
            'Family history of diabetes'
          ],
          recommendedActions: [
            'Reduce sugar and refined carbohydrate intake',
            'Increase physical activity to 150+ minutes per week',
            'Lose 5-10% body weight if overweight',
            'Schedule fasting blood sugar and HbA1c tests',
            'Monitor blood sugar levels every 6 months',
            'Consider lifestyle counseling programs',
            'Discuss metformin or other prevention medications with doctor'
          ],
          dietRecommendations: {
            foodsToEat: [
              'Non-starchy vegetables',
              'Whole grains (quinoa, oats, whole wheat)',
              'Lean proteins (fish, chicken, legumes)',
              'High-fiber foods',
              'Low-glycemic index foods'
            ],
            foodsToAvoid: [
              'Sugary drinks and beverages',
              'White bread and white rice',
              'Processed snacks',
              'Excessive alcohol'
            ]
          },
          lifestyleRecommendations: [
            'Exercise 150 minutes per week (moderate)',
            'Include strength training twice weekly',
            'Take walks after meals',
            'Get adequate sleep (7-8 hours)',
            'Manage stress levels'
          ],
          additionalSupport: [
            'Join diabetes prevention program (DPP)',
            'Regular health check-ups every 6 months',
            'Work with dietitian for personalized meal plan',
            'Annual blood sugar screening'
          ]
        }
      ];
    }
    return [
      {
        title: 'Low Risk - Normal Blood Sugar',
        riskLevel: 'Low',
        riskFactors: [],
        recommendedActions: [
          'Maintain healthy lifestyle with regular physical activity',
          'Continue monitoring blood sugar levels annually',
          'Follow a balanced diet rich in fiber and whole grains',
          'Maintain healthy body weight',
          'Continue regular check-ups with healthcare provider'
        ],
        dietRecommendations: {
          foodsToEat: [
            'Balanced diet with variety of nutrients',
            'Whole grains and fiber',
            'Lean proteins',
            'Fruits and vegetables'
          ],
          foodsToAvoid: []
        },
        lifestyleRecommendations: [
          'Regular physical activity',
          'Healthy sleep patterns',
          'Stress management',
          'Avoid smoking'
        ],
        additionalSupport: [
          'Annual screening for blood sugar',
          'Maintain healthy weight',
          'Regular check-ups'
        ]
      }
    ];
  };

  const getAnemiaRecommendations = (riskCategory) => {
    if (riskCategory === 'high') {
      return [
        {
          title: 'High Risk - Severe Anemia',
          riskLevel: 'High',
          riskFactors: [
            '⚠️ Hemoglobin < 10 g/dL (Severe anemia)',
            '⚠️ Low Vitamin B12 (<200 pg/mL)',
            '⚠️ Low iron intake confirmed',
            'Significant fatigue symptoms'
          ],
          recommendedActions: [
            '⚠️ Consult hematologist immediately',
            'Consider iron infusion therapy',
            'Test for GI bleeding/malabsorption',
            'Vitamin B12 injections if deficient',
            'Hospitalization if hemoglobin <7 g/dL',
            'Complete blood count follow-up weekly'
          ],
          dietRecommendations: {
            foodsToEat: [
              'Red meat (beef, lamb - highest heme iron)',
              'Liver (beef/chicken liver - iron + B12)',
              'Poultry (dark meat preferred)',
              'Fish/shellfish (oysters, clams, mussels)',
              'Leafy greens (spinach with lemon juice)',
              'Legumes (lentils, chickpeas with vitamin C)'
            ],
            foodsToAvoid: [
              'Tea/coffee with meals (inhibits iron absorption)',
              'Calcium-rich foods during iron meals (dairy)',
              'High-fiber bran during iron intake',
              'Alcohol (impairs absorption)'
            ]
          },
          lifestyleRecommendations: [
            'Space iron-rich meals 1 hour from tea/coffee/calcium',
            'Pair iron foods with vitamin C sources (lemon/oranges)',
            'Cook in cast iron pans for extra iron',
            'Avoid NSAIDs if GI bleeding risk',
            'Gentle exercise to combat fatigue'
          ],
          additionalSupport: [
            'Iron supplementation (ferrous sulfate 325mg daily)',
            'Vitamin B12 injections (1000mcg weekly x 8)',
            'Folate supplementation (1mg daily)',
            'Reticulocyte count monitoring',
            'Ferritin, TIBC, transferrin saturation tests'
          ]
        }
      ];
    } else if (riskCategory === 'moderate') {
      return [
        {
          title: 'Moderate Risk - Mild/Moderate Anemia',
          riskLevel: 'Moderate',
          riskFactors: [
            'Hemoglobin 10-12 g/dL (mild anemia)',
            'Low-normal iron intake',
            'Vegetarian/vegan diet risks',
            'Moderate fatigue symptoms'
          ],
          recommendedActions: [
            'Consult primary care physician',
            'Start oral iron supplementation',
            'Repeat CBC in 4 weeks',
            'Dietary counseling',
            'Vitamin B12/folate testing'
          ],
          dietRecommendations: {
            foodsToEat: [
              'Fortified cereals (check iron content)',
              'Spinach + lemon juice (vitamin C enhances absorption)',
              'Lentils + tomatoes',
              'Tofu/quinoa (vegetarian iron sources)',
              'Pumpkin seeds, sesame seeds'
            ],
            foodsToAvoid: [
              'Tea/coffee within 1 hour of meals',
              'Calcium supplements with iron foods'
            ]
          },
          lifestyleRecommendations: [
            'Vitamin C with every iron-rich meal',
            'Light exercise (walking/yoga)',
            'Stress management (fatigue worsens anemia)'
          ],
          additionalSupport: [
            'Ferrous sulfate 325mg daily (take with orange juice)',
            'Follow-up blood tests in 4 weeks',
            'Consider slow-release iron if stomach upset'
          ]
        }
      ];
    }
    return [
      {
        title: 'Low Risk - Normal Hemoglobin',
        riskLevel: 'Low',
        riskFactors: [],
        recommendedActions: [
          'Maintain current iron-rich diet',
          'Annual CBC screening',
          'Continue current supplementation if any'
        ],
        dietRecommendations: {
          foodsToEat: [
            'Balanced diet with varied iron sources',
            'Include vitamin C-rich foods daily'
          ],
          foodsToAvoid: []
        },
        lifestyleRecommendations: [
          'Regular physical activity',
          'Adequate hydration'
        ],
        additionalSupport: [
          'Annual hemoglobin screening'
        ]
      }
    ];
  };

  const getHeartRecommendations = (riskCategory) => {
    if (riskCategory === 'high') {
      return [
        {
          title: 'High Risk - Immediate Cardiovascular Threat',
          riskLevel: 'High',
          riskFactors: [
            '⚠️ Systolic BP ≥140 mmHg (Hypertension)',
            '⚠️ Total cholesterol ≥240 mg/dL',
            '⚠️ Current smoking status',
            'Multiple risk factors combined'
          ],
          recommendedActions: [
            '⚠️ Consult cardiologist within 24-48 hours',
            '24-hour blood pressure monitoring',
            'Lipid panel + ECG + stress test',
            'Smoking cessation program IMMEDIATE',
            'Statins if LDL >130 mg/dL',
            'Consider aspirin therapy'
          ],
          dietRecommendations: {
            foodsToEat: [
              'Fatty fish (salmon, mackerel - omega 3)',
              'Oats/oatmeal (soluble fiber lowers cholesterol)',
              'Nuts (almonds, walnuts - 1oz daily)',
              'Leafy greens (spinach, kale)',
              'Berries (antioxidants)',
              'Avocados (healthy monounsaturated fats)',
              'Olive oil (replace butter)'
            ],
            foodsToAvoid: [
              'Trans fats (fried foods, margarine)',
              'Processed meats (bacon, sausage)',
              'Sugary drinks/foods',
              'Excess sodium (>2300mg/day)',
              'Red meat >2x/week'
            ]
          },
          lifestyleRecommendations: [
            'Smoking cessation counseling TODAY',
            '30 minutes daily walking minimum',
            'Stress reduction (meditation)',
            'Sleep 7-9 hours nightly',
            'Weight loss 5-10% if overweight'
          ],
          additionalSupport: [
            'Home BP monitoring daily',
            'Cholesterol check every 3 months',
            'Cardiac risk calculator (ASCVD)',
            'Consider cardiac rehab program'
          ]
        }
      ];
    } else if (riskCategory === 'moderate') {
      return [
        {
          title: 'Moderate Risk - Elevated Cardiovascular Risk',
          riskLevel: 'Moderate',
          riskFactors: [
            'Borderline high BP (130-139/80-89)',
            'Borderline cholesterol (200-239 mg/dL)',
            'Overweight BMI',
            'Sedentary lifestyle'
          ],
          recommendedActions: [
            'Schedule cardiovascular check-up',
            'Begin lifestyle modification program',
            'Repeat lipid panel in 3 months',
            'Blood pressure monitoring',
            'Smoking cessation if applicable'
          ],
          dietRecommendations: {
            foodsToEat: [
              'Whole grains (brown rice, quinoa)',
              'Legumes (beans, lentils)',
              'Fruits (apples, oranges)',
              'Vegetables (broccoli, carrots)',
              'Skinless poultry/fish'
            ],
            foodsToAvoid: [
              'Fried foods',
              'Excessive salt',
              'Sugary beverages'
            ]
          },
          lifestyleRecommendations: [
            '150 minutes moderate exercise/week',
            'Strength training 2x/week',
            'Stress management techniques',
            '7-9 hours sleep nightly'
          ],
          additionalSupport: [
            'Home BP monitor',
            'Dietitian consultation',
            'Annual cardiovascular screening'
          ]
        }
      ];
    }
    return [
      {
        title: 'Low Risk - Heart Healthy',
        riskLevel: 'Low',
        riskFactors: [],
        recommendedActions: [
          'Continue heart-healthy lifestyle',
          'Annual cardiovascular screening',
          'Maintain ideal body weight'
        ],
        dietRecommendations: {
          foodsToEat: [
            'Mediterranean diet pattern',
            'Plenty of fruits/vegetables',
            'Healthy fats (olive oil, nuts)'
          ],
          foodsToAvoid: []
        },
        lifestyleRecommendations: [
          'Regular aerobic exercise',
          'Stress management',
          'No smoking'
        ],
        additionalSupport: [
          'Annual check-up',
          'Know family history'
        ]
      }
    ];
  };

  const handleVitaminDSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    const riskAssessment = calculateVitaminDRisk();
    const personalizedRecs = getVitaminDRecommendations(riskAssessment.riskCategory);
    const allData = { ...formData, ...vitaminDData };
    localStorage.setItem('healthData', JSON.stringify(allData));
    localStorage.setItem('risks', JSON.stringify({ vitamind: riskAssessment.riskLevel }));
    setRecommendations({ disease: 'vitaminD', diseaseName: 'Vitamin D', riskAssessment, recommendations: personalizedRecs });
    setLoading(false);
  };

  const [apiError, setApiError] = useState('');

  const handleDiabetesSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setApiError('');
    
    try {
      const allData = { 
        ...formData, 
        ...diabetesData,
        familyHistoryDiabetes: diabetesData.familyHistoryDiabetes || 'no'
      };
      
      const response = await fetch('http://localhost:5000/api/diabetes-predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(allData)
      });
      
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      
      const apiResult = await response.json();
      
      const riskAssessment = {
        riskLevel: apiResult.rule_based.riskLevel || 'Low',
        riskCategory: apiResult.rule_based.riskLevel.toLowerCase(),
        riskScore: apiResult.rule_based.riskScore || 0,
        factors: apiResult.rule_based.recommendations || []
      };
      
      const personalizedRecs = [{
        title: `${apiResult.rule_based.riskLevel} Diabetes Risk`,
        riskLevel: apiResult.rule_based.riskLevel,
        riskFactors: riskAssessment.factors.slice(0,5), // Limit factors
        recommendedActions: apiResult.rule_based.recommendations || [],
        ...(apiResult.config_recs.diet || {}),
        ...(apiResult.config_recs.lifestyle || {}),
        ...(apiResult.config_recs.actions || {}),
        mlPrediction: apiResult.ml_based.prediction || 'N/A',
        mlProbabilities: apiResult.ml_based.probabilities || {}
      }];
      
      localStorage.setItem('healthData', JSON.stringify(allData));
      localStorage.setItem('risks', JSON.stringify({ diabetes: riskAssessment.riskLevel }));
      
      setRecommendations({ 
        disease: 'diabetes', 
        diseaseName: 'Diabetes', 
        riskAssessment, 
        recommendations: personalizedRecs 
      });
      
    } catch (error) {
      console.error('Diabetes API error:', error);
      setApiError(`Failed to fetch diabetes prediction: ${error.message}`);
      // Fallback to local calculation
      const riskAssessment = calculateDiabetesRisk();
      const personalizedRecs = getDiabetesRecommendations(riskAssessment.riskCategory);
      setRecommendations({ disease: 'diabetes', diseaseName: 'Diabetes', riskAssessment, recommendations: personalizedRecs });
    } finally {
      setLoading(false);
    }
  };


  const handleAnemiaSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    const riskAssessment = calculateAnemiaRisk();
    const personalizedRecs = getAnemiaRecommendations(riskAssessment.riskCategory);
    const allData = { ...formData, ...anemiaData };
    localStorage.setItem('healthData', JSON.stringify(allData));
    localStorage.setItem('risks', JSON.stringify({ anemia: riskAssessment.riskLevel }));
    setRecommendations({ disease: 'anemia', diseaseName: 'Anemia Risk', riskAssessment, recommendations: personalizedRecs });
    updateDynamicRecommendations('anemia');
    setLoading(false);
  };

  const handleHeartSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    const riskAssessment = calculateHeartRisk();
    const personalizedRecs = getHeartRecommendations(riskAssessment.riskCategory);
    const allData = { ...formData, ...heartData };
    localStorage.setItem('healthData', JSON.stringify(allData));
    localStorage.setItem('risks', JSON.stringify({ heart: riskAssessment.riskLevel }));
    setRecommendations({ disease: 'heart', diseaseName: 'Heart Risk', riskAssessment, recommendations: personalizedRecs });
    updateDynamicRecommendations('heart');
    setLoading(false);
  };

  return (
    <div className="dashboard-container">
      <div className="header">
        <div className="header-icons">
          <i className="fas fa-heart"></i>
          <i className="fas fa-stethoscope"></i>
        </div>
        <div className="header-title">Healthcare Recommendation System</div>
      </div>
      
      <div className="main-content">
        {showDynamicRecs && dynamicRecommendations.length > 0 && !recommendations && (
          <div className="dynamic-recs-banner" style={{ backgroundColor: '#e3f2fd', border: '2px solid #2196F3', borderRadius: '8px', padding: '15px', marginBottom: '20px' }}>
            <h4 style={{margin: '0 0 10px 0', color: '#1565C0'}}>Live Recommendations</h4>
            <ul style={{margin: 0, paddingLeft: '20px'}}>
              {dynamicRecommendations.map((rec, index) => (<li key={index} style={{marginBottom: '5px'}}>{rec}</li>))}
            </ul>
          </div>
        )}

        <div className="cards-row">
          <div className={`card vitamin-d ${expandedSections.vitaminD ? 'active' : ''}`} onClick={() => toggleSection('vitaminD')}>
            <i className="fas fa-sun card-icon"></i>
            <h3 className="card-title">Vitamin D Risk</h3>
            {expandedSections.vitaminD ? <span className="card-toggle">-</span> : <span className="card-toggle">+</span>}
          </div>
          
          <div className={`card diabetes ${expandedSections.diabetes ? 'active' : ''}`} onClick={() => toggleSection('diabetes')}>
            <i className="fas fa-syringe card-icon"></i>
            <h3 className="card-title">Diabetes Risk</h3>
            {expandedSections.diabetes ? <span className="card-toggle">-</span> : <span className="card-toggle">+</span>}
          </div>
          
          <div className={`card anemia ${expandedSections.anemia ? 'active' : ''}`} onClick={() => toggleSection('anemia')}>
            <i className="fas fa-tint card-icon"></i>
            <h3 className="card-title">Anemia Risk</h3>
            {expandedSections.anemia ? <span className="card-toggle">-</span> : <span className="card-toggle">+</span>}
          </div>
          
          <div className={`card heart ${expandedSections.heart ? 'active' : ''}`} onClick={() => toggleSection('heart')}>
            <i className="fas fa-heartbeat card-icon"></i>
            <h3 className="card-title">Heart Risk</h3>
            {expandedSections.heart ? <span className="card-toggle">-</span> : <span className="card-toggle">+</span>}
          </div>
        </div>

        {expandedSections.vitaminD && !recommendations && (
          <div className="form-section expanded">
            <div className="form-container">
              <h2 className="form-title">Vitamin D Assessment</h2>
              <form onSubmit={handleVitaminDSubmit}>
                <h3 className="form-section-title">Basic Information</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Age *</label>
                    <input type="number" name="age" value={formData.age} onChange={handleCommonChange} className="form-input" placeholder="Enter your age" required />
                    <small className="form-hint">Hint: Enter your age in years (e.g., 35)</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Gender *</label>
                    <select name="gender" value={formData.gender} onChange={handleCommonChange} className="form-select" required>
                      <option value="">Select gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </select>
                    <small className="form-hint">Hint: Select your biological gender</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Location</label>
                    <input type="text" name="location" value={vitaminDData.location} onChange={handleVitaminDChange} className="form-input" placeholder="Enter your city/country" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Height (cm)</label>
                    <input type="number" name="height" value={formData.height} onChange={handleCommonChange} className="form-input" placeholder="Enter height in cm" />
                    <small className="form-hint">Hint: Enter height in centimeters (e.g., 170)</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Weight (kg)</label>
                    <input type="number" name="weight" value={formData.weight} onChange={handleCommonChange} className="form-input" placeholder="Enter weight in kg" />
                    <small className="form-hint">Hint: Enter weight in kilograms (e.g., 70)</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">BMI (Auto-calculated)</label>
                    <input type="number" name="bmi" value={formData.bmi} className="form-input" readOnly placeholder="Auto-calculated from height/weight" />
                    <small className="form-hint">✅ BMI syncs automatically across all forms</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Smoking Status</label>
                    <select name="smokingStatus" value={vitaminDData.smokingStatus} onChange={handleVitaminDChange} className="form-select">
                      <option value="">Select smoking status</option>
                      <option value="yes">Yes</option>
                      <option value="no">No</option>
                    </select>
                    <small className="form-hint">Hint: Do you currently smoke?</small>
                  </div>
                </div>

                <h3 className="form-section-title">Lifestyle</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Alcohol Consumption</label>
                    <select name="alcoholConsumption" value={vitaminDData.alcoholConsumption} onChange={handleVitaminDChange} className="form-select">
                      <option value="">Select alcohol consumption</option>
                      <option value="none">None</option>
                      <option value="moderate">Moderate</option>
                      <option value="heavy">Heavy</option>
                    </select>
                    <small className="form-hint">Hint: None (0 drinks/week), Moderate (1-7 drinks/week), Heavy (8+ drinks/week)</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Exercise Level</label>
                    <select name="exerciseLevel" value={vitaminDData.exerciseLevel} onChange={handleVitaminDChange} className="form-select">
                      <option value="">Select exercise level</option>
                      <option value="none">None</option>
                      <option value="occasional">Occasional (1-2 days/week)</option>
                      <option value="regular">Regular (3-5 days/week)</option>
                    </select>
                    <small className="form-hint">Hint: How often do you exercise per week?</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Diet Type</label>
                    <select name="dietType" value={vitaminDData.dietType} onChange={handleVitaminDChange} className="form-select">
                      <option value="">Select diet type</option>
                      <option value="vegetarian">Vegetarian</option>
                      <option value="non-vegetarian">Non-Vegetarian</option>
                      <option value="vegan">Vegan</option>
                      <option value="mixed">Mixed</option>
                    </select>
                    <small className="form-hint">Hint: Select your dietary preference</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Sun Exposure (hours/day)</label>
                    <input type="number" name="sunExposure" value={vitaminDData.sunExposure} onChange={handleVitaminDChange} className="form-input" placeholder="Enter sun exposure hours" step="0.5" />
                    <small className="form-hint">Hint: Average daily sun exposure in hours (e.g., 1.5)</small>
                  </div>
                </div>

                <h3 className="form-section-title">Lab Values</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Vitamin D % RDA</label>
                    <input type="number" name="vitaminDPercentRda" value={vitaminDData.vitaminDPercentRda} onChange={handleVitaminDChange} className="form-input" placeholder="Enter Vitamin D % RDA" />
                    <small className="form-hint">Hint: Percentage of Recommended Daily Allowance (100% = 600 IU)</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Calcium % RDA</label>
                    <input type="number" name="calciumPercentRda" value={vitaminDData.calciumPercentRda} onChange={handleVitaminDChange} className="form-input" placeholder="Enter Calcium % RDA" />
                    <small className="form-hint">Hint: Percentage of Recommended Daily Allowance for Calcium (100% = 1000mg)</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Iron % RDA</label>
                    <input type="number" name="ironPercentRda" value={vitaminDData.ironPercentRda} onChange={handleVitaminDChange} className="form-input" placeholder="Enter Iron % RDA" />
                    <small className="form-hint">Hint: Percentage of Recommended Daily Allowance for Iron (100% = 18mg)</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Hemoglobin (g/dL)</label>
                    <input type="number" name="hemoglobinGdl" value={vitaminDData.hemoglobinGdl} onChange={handleVitaminDChange} className="form-input" placeholder="Enter Hemoglobin level" step="0.1" />
                    <small className="form-hint">Hint: Normal: Male 13.5-17.5, Female 12-16 g/dL</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Serum Vitamin D (ng/mL)</label>
                    <input type="number" name="serumVitaminDNgml" value={vitaminDData.serumVitaminDNgml} onChange={handleVitaminDChange} className="form-input" placeholder="Enter Serum Vitamin D" />
                    <small className="form-hint">Hint: Normal: 30-100 ng/mL, Deficient: </small>
                  </div>
                </div>

                <button type="submit" className="submit-button" disabled={loading}>
                  {loading ? 'Calculating...' : 'Get Vitamin D Recommendations'}
                </button>
              </form>
            </div>
          </div>
        )}

        {expandedSections.diabetes && !recommendations && (
          <div className="form-section expanded">
            <div className="form-container">
              <h2 className="form-title">Diabetes Risk Prediction</h2>
              <form onSubmit={handleDiabetesSubmit}>
                <h3 className="form-section-title">Basic Information</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Age *</label>
                    <input type="number" name="age" value={formData.age || diabetesData.age} onChange={handleDiabetesCommonChange} className="form-input" required />
                    <small className="form-hint">Enter age in years</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Gender *</label>
                    <select name="gender" value={formData.gender || diabetesData.gender} onChange={handleDiabetesCommonChange} className="form-select" required>
                      <option value="">Select</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </select>
                    <small className="form-hint">Biological gender affects risk factors</small>
                  </div>
                   <div className="form-group">
                    <label className="form-label">Location</label>
                    <input type="text" name="location" value={diabetesData.location} onChange={handleDiabetesChange} className="form-input" placeholder="e.g., Mumbai, India" />
                    <small className="form-hint">Free text - city/region</small>
                  </div>
                    <div className="form-group">
                    <label className="form-label">Height (cm)</label>
                    <input type="number" name="height" value={diabetesData.height || formData.height} onChange={handleDiabetesChange} className="form-input" placeholder="170" step="0.1" />
                    <small className="form-hint">Required for BMI calculation (syncs automatically)</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Weight (kg)</label>
                    <input type="number" name="weight" value={diabetesData.weight || formData.weight} onChange={handleDiabetesChange} className="form-input" placeholder="70" step="0.1" />
                    <small className="form-hint">Required for BMI calculation</small>
                  </div>
                    <div className="form-group">
                    <label className="form-label">BMI (Auto-calculated)</label>
                    <input type="number" name="bmi" value={formData.bmi} onChange={handleCommonChange} className="form-input" readOnly placeholder="Auto-calculated" />
                    <small className="form-hint">Hint: BMI is automatically calculated from height and weight</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Family History of Diabetes</label>
                    <select name="familyHistoryDiabetes" value={diabetesData.familyHistoryDiabetes} onChange={handleDiabetesChange} className="form-select">
                      <option value="">Select</option>
                      <option value="yes">Yes</option>
                      <option value="no">No</option>
                      <option value="unknown">Unknown</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Physical Activity</label>
                    <select name="physicalActivity" value={formData.physicalActivity} onChange={handleCommonChange} className="form-select">
                      <option value="">Select</option>
                      <option value="sedentary">Sedentary</option>
                      <option value="occasional">Occasional</option>
                      <option value="moderate">Moderate</option>
                      <option value="active">Active</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Smoking Status</label>
                    <select name="smokingStatus" value={formData.smokingStatus} onChange={handleCommonChange} className="form-select">
                      <option value="">Select</option>
                      <option value="yes">Yes</option>
                      <option value="no">No</option>
                    </select>
                  </div>
                </div>
                <h3 className="form-section-title">Blood Sugar</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Fasting Blood Sugar (mg/dL)</label>
                    <input type="number" name="fastingBloodSugar" value={diabetesData.fastingBloodSugar} onChange={handleDiabetesChange} className="form-input" placeholder="Normal: 70-100" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">HbA1c Level (%)</label>
                    <input type="number" name="hbA1cLevel" value={diabetesData.hbA1cLevel} onChange={handleDiabetesChange} className="form-input" placeholder="Normal: <5.7%" step="0.1" />
                  </div>
                </div>

                <button type="submit" className="submit-button" disabled={loading}>
                  {loading ? 'Calculating...' : 'Get Diabetes Recommendations'}
                </button>
              </form>
            </div>
          </div>
        )}

        {expandedSections.anemia && !recommendations && (
          <div className="form-section expanded">
            <div className="form-container">
              <h2 className="form-title">Anemia Risk Assessment</h2>
              <form onSubmit={handleAnemiaSubmit}>
                <h3 className="form-section-title">Basic Information</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Age *</label>
                    <input type="number" name="age" value={formData.age} onChange={handleCommonChange} className="form-input" required />
                    <small className="form-hint">Enter age in years</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Gender *</label>
                    <select name="gender" value={formData.gender} onChange={handleCommonChange} className="form-select" required>
                      <option value="">Select</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </select>
                    <small className="form-hint">Affects hemoglobin reference ranges</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Location</label>
                    <input type="text" name="location" value={anemiaData.location} onChange={handleAnemiaChange} className="form-input" placeholder="e.g., Mumbai, India" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Height (cm)</label>
                    <input type="number" name="height" value={formData.height} onChange={handleCommonChange} className="form-input" placeholder="170" step="0.1" />
                    <small className="form-hint">Required for BMI calculation</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Weight (kg)</label>
                    <input type="number" name="weight" value={formData.weight} onChange={handleCommonChange} className="form-input" placeholder="70" step="0.1" />
                    <small className="form-hint">Required for BMI calculation</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">BMI (Auto-calculated)</label>
                    <input type="number" name="bmi" value={formData.bmi} className="form-input" readOnly placeholder="Auto-calculated" />
                    <small className="form-hint">BMI = weight / (height/100)²</small>
                  </div>
                </div>

<h3 className="form-section-title">Health Information</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Hemoglobin Level (g/dL) *</label>
                    <input type="number" name="hemoglobinGdl" value={anemiaData.hemoglobinGdl} onChange={handleAnemiaChange} className="form-input" placeholder="Normal: Male 13.5-17.5, Female 12-16" step="0.1" required />
                    <small className="form-hint">Enter hemoglobin level from recent blood test</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Iron Intake</label>
                    <select name="ironIntake" value={anemiaData.ironIntake} onChange={handleAnemiaChange} className="form-select">
                      <option value="">Select</option>
                      <option value="low">Low ( 8mg/day)</option>
                      <option value="moderate">Moderate (8-18mg/day)</option>
                      <option value="adequate">Adequate (18mg/day)</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Diet *</label>
                    <select name="diet" value={anemiaData.diet} onChange={handleAnemiaChange} className="form-select" required>
                      <option value="">Select diet type</option>
                      <option value="vegetarian">Vegetarian</option>
                      <option value="non-vegetarian">Non-Vegetarian</option>
                      <option value="vegan">Vegan</option>
                    </select>
                    <small className="form-hint">Vegetarian diets may need more attention to iron/B12 sources</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Vitamin B12 Level (pg/mL)</label>
                    <input type="number" name="vitaminB12Level" value={anemiaData.vitaminB12Level} onChange={handleAnemiaChange} className="form-input" placeholder="Normal: 200-900 pg/mL" step="10" />
                    <small className="form-hint">Low B12 can cause pernicious anemia</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Fatigue Symptoms</label>
                    <select name="fatigueSymptoms" value={anemiaData.fatigueSymptoms} onChange={handleAnemiaChange} className="form-select">
                      <option value="">Select</option>
                      <option value="none">None</option>
                      <option value="mild">Mild</option>
                      <option value="moderate">Moderate</option>
                      <option value="severe">Severe</option>
                    </select>
                    <small className="form-hint">Common anemia symptom indicator</small>
                  </div>
                </div>

                <button type="submit" className="submit-button" disabled={loading}>
                  {loading ? 'Calculating...' : 'Get Anemia Recommendations'}
                </button>
              </form>
            </div>
          </div>
        )}

        {expandedSections.heart && !recommendations && (
          <div className="form-section expanded">
            <div className="form-container">
              <h2 className="form-title">Heart Risk Assessment</h2>
              <form onSubmit={handleHeartSubmit}>
<h3 className="form-section-title">Basic Information</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Age *</label>
                    <input type="number" name="age" value={formData.age} onChange={handleCommonChange} className="form-input" required />
                    <small className="form-hint">Age is major cardiovascular risk factor</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Gender *</label>
                    <select name="gender" value={formData.gender} onChange={handleCommonChange} className="form-select" required>
                      <option value="">Select</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </select>
                    <small className="form-hint">Risk factors vary by gender</small>
                  </div><div className="form-group">
                    <label className="form-label">Location</label>
                    <input type="text" name="location" value={heartData.location} onChange={handleHeartChange} className="form-input" placeholder="Enter city/region" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Height (cm)</label>
                    <input type="number" name="height" value={formData.height} onChange={handleCommonChange} className="form-input" placeholder="170" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Weight (kg)</label>
                    <input type="number" name="weight" value={formData.weight} onChange={handleCommonChange} className="form-input" placeholder="70" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">BMI (Auto)</label>
                    <input type="number" name="bmi" value={formData.bmi} className="form-input" readOnly />
                    <small className="form-hint">Auto-calculated. Obesity major risk</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Smoking Status *</label>
                    <select name="smokingStatus" value={formData.smokingStatus} onChange={handleCommonChange} className="form-select" required>
                      <option value="">Select</option>
                      <option value="never">Never smoked</option>
                      <option value="current">Current smoker</option>
                      <option value="former">Former smoker</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Physical Activity *</label>
                    <select name="physicalActivity" value={formData.physicalActivity} onChange={handleCommonChange} className="form-select" required>
                      <option value="">Select</option>
                      <option value="sedentary">Sedentary</option>
                      <option value="light">Light activity</option>
                      <option value="moderate">Moderate</option>
                      <option value="vigorous">Vigorous</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Family History *</label>
                    <select name="familyHistory" value={heartData.familyHistory} onChange={handleHeartChange} className="form-select" required>
                      <option value="">Select</option>
                      <option value="no">No family history</option>
                      <option value="parent">Parent affected</option>
                      <option value="sibling">Sibling affected</option>
                      <option value="multiple">Multiple family members</option>
                    </select>
                    <small className="form-hint">Strong genetic risk factor</small>
                  </div>
                </div>

<h3 className="form-section-title">Vital Signs & Labs</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Systolic BP (mmHg) *</label>
                    <input type="number" name="systolicBP" value={heartData.systolicBP} onChange={handleHeartChange} className="form-input" placeholder="Normal: <120" required />
                    <small className="form-hint">High BP major risk factor</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Diastolic BP (mmHg) *</label>
                    <input type="number" name="diastolicBP" value={heartData.diastolicBP} onChange={handleHeartChange} className="form-input" placeholder="Normal: <80" required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Blood Sugar (mg/dL)</label>
                    <input type="number" name="bloodSugar" value={heartData.bloodSugar} onChange={handleHeartChange} className="form-input" placeholder="Fasting: 70-100" step="5" />
                    <small className="form-hint">Diabetes increases heart risk</small>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Total Cholesterol (mg/dL)</label>
                    <input type="number" name="totalCholesterol" value={heartData.totalCholesterol} onChange={handleHeartChange} className="form-input" placeholder="Optimal: <200" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">HDL Cholesterol (mg/dL)</label>
                    <input type="number" name="hdlCholesterol" value={heartData.hdlCholesterol} onChange={handleHeartChange} className="form-input" placeholder="Good: Men >40, Women >50" />
                  </div>
                </div>

                <button type="submit" className="submit-button" disabled={loading}>
                  {loading ? 'Calculating...' : 'Get Heart Recommendations'}
                </button>
              </form>
            </div>
          </div>
        )}

        {recommendations && (
          <div className="recommendations-result">
            <div className="risk-summary">
              <div className={`risk-level ${recommendations.riskAssessment.riskCategory}`}>
                <h2>{recommendations.diseaseName} Risk Level: {recommendations.riskAssessment.riskLevel}</h2>
                <p>Risk Score: {recommendations.riskAssessment.riskScore}</p>
              </div>
              
              <div className="risk-factors">
                <h3>Risk Factors Identified:</h3>
                <ul>
                  {recommendations.riskAssessment.factors.map((factor, index) => (
                    <li key={index} className={factor.severity}>{factor.factor}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="personalized-recs">
              {recommendations.recommendations.map((recGroup, index) => (
                <div key={index} className="rec-group">
                  <h3>{recGroup.title}</h3>
                  
                  {/* Recommended Actions */}
                  {recGroup.recommendedActions && recGroup.recommendedActions.length > 0 && (
                    <div className="rec-subsection">
                      <h4>Recommended Actions:</h4>
                      <ul>
                        {recGroup.recommendedActions.map((action, idx) => (
                          <li key={idx}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Diet Recommendations */}
                  {recGroup.dietRecommendations && (
                    <div className="rec-subsection">
                      <h4>Diet Recommendations:</h4>
                      {recGroup.dietRecommendations.foodsToEat && recGroup.dietRecommendations.foodsToEat.length > 0 && (
                        <div className="foods-section">
                          <h5>Foods to Eat:</h5>
                          <ul>
                            {recGroup.dietRecommendations.foodsToEat.map((food, idx) => (
                              <li key={idx} className="food-to-eat">{food}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {recGroup.dietRecommendations.foodsToAvoid && recGroup.dietRecommendations.foodsToAvoid.length > 0 && (
                        <div className="foods-section">
                          <h5>Foods to Avoid:</h5>
                          <ul>
                            {recGroup.dietRecommendations.foodsToAvoid.map((food, idx) => (
                              <li key={idx} className="food-to-avoid">{food}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Lifestyle Recommendations */}
                  {recGroup.lifestyleRecommendations && recGroup.lifestyleRecommendations.length > 0 && (
                    <div className="rec-subsection">
                      <h4>Lifestyle Recommendations:</h4>
                      <ul>
                        {recGroup.lifestyleRecommendations.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Additional Support */}
                  {recGroup.additionalSupport && recGroup.additionalSupport.length > 0 && (
                    <div className="rec-subsection additional-support">
                      <h4>Additional Support:</h4>
                      <ul>
                        {recGroup.additionalSupport.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Fallback to old format if items exists */}
                  {recGroup.items && (
                    <ul>
                      {recGroup.items.map((item, idx) => (<li key={idx}>{item}</li>))}
                    </ul>
                  )}
                </div>
              ))}
            </div>

            <div className="results-actions">
              <button className="submit-button secondary" onClick={() => setRecommendations(null)}>
                Back to Forms
              </button>
              <Link to="/report" className="submit-button primary">
                View Health Report
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

