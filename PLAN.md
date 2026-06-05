# Plan: Update Vitamin D and Diabetes Input Fields

## Information Gathered:
Based on code analysis of Dashboard.js:
- **Vitamin D Section** has: dietType, sunExposure, vitaminDPercentRda, calciumPercentRda, serumVitaminDNgml, alcoholConsumption, exerciseLevel, ironPercentRda, hemoglobin
- **Diabetes Section** has: fastingBloodSugar, hbA1cLevel, systolicBP, diastolicBP, totalCholesterol, hdlCholesterol
- ironPercentRda and hemoglobin are wrongly placed in Vitamin D (they are anemia-related)

## Plan:

### 1. Remove incorrect fields from Vitamin D section:
- Remove: `ironPercentRda` (anemia-related, not vitamin D)
- Remove: `hemoglobin` (anemia-related, not vitamin D)

### 2. Add MORE important input fields to Vitamin D:
- `age` - Important for vitamin D absorption/decline
- `skinType` - Darker skin reduces synthesis
- `latitude` - Geographic location affects UV exposure
- `useSunscreen` - Blocks vitamin D synthesis
- `clothingStyle` - Coverage affects sun exposure
- `kidneyFunction` - Affects vitamin D metabolism
- `parathyroidHormone` - PTH regulates vitamin D
- `magnesiumLevel` - Needed for vitamin D activation

### 3. Add MORE important input fields to Diabetes:
- `familyHistory` - Genetic predisposition
- `waistCircumference` - Central obesity marker
- `cReactiveProtein` - Inflammatory marker
- `fastingInsulin` - Insulin resistance
- `randomBloodSugar` - Additional glucose measure
- `polyuria` - Diabetes symptom
- `polydipsia` - Diabetes symptom
- `weightLoss` - Diabetes symptom

### 4. Update related functions:
- Update `vitaminDData` useState initialization
- Update `diabetesData` useState initialization
- Update handleVitaminDChange function
- Update handleDiabetesChange function
- Update recommendation functions
- Update risk calculation functions
- Update form rendering JSX

## Dependent Files to be edited:
- `src/components/Dashboard.js` - Main file with input fields

## Followup steps:
1. Apply the edits to Dashboard.js
2. Test the application to ensure it runs correctly
</parameter>
</create_file>
