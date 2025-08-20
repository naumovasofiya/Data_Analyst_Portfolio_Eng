# Analysis of Stress Levels Among Students

**Notebook link:** `students_stress_level.ipynb`

## Research Objective

To conduct a comprehensive analysis of stress factors among students, identify key indicators, and develop recommendations for reducing stress load.

## Key Research Questions

1. What types of stress predominate among students?
2. Which symptoms correlate most strongly with stress levels?
3. How does age affect stress levels?
4. Which academic factors are most significant for predicting stress?
5. How is sleep quality related to stress levels?

## Main Hypotheses

1. Academic workload is a key stress factor
2. Sleep problems increase stress levels
3. Social support reduces distress levels
4. Eustress (positive stress) predominates over distress

## Libraries Used

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `scipy`

## Datasets Used

- **Dataset 1:** Survey data on stress symptoms (11 indicators)
- **Dataset 2:** Structured stress data (8 psychological and academic indicators)

## Research Results

### 1. Data Preparation and Processing
Two different datasets were loaded and standardized. A categorical variable `stress_type` was created for both datasets. No missing values were present.

### 2. Stress Type Distribution
Significant differences were found between datasets:
- **Dataset 1:** Eustress predominates (91.1%)
- **Dataset 2:** Even distribution (approximately 30% for each type)

### 3. Age Analysis
- Students with distress are slightly older on average (median 22 years)
- Eustress is more common at ages 20-21
- Upper-year students experience more negative stress

### 4. Symptom Analysis
- Students with distress have significantly higher total symptom scores
- Students with eustress show moderate symptom levels
- Students without stress have minimal symptom manifestations

### 5. Correlation Analysis
**Strongest stress factors:**
- **Bullying** (corr. 0.751) - the most destructive factor
- **Career future anxiety** (0.743)
- **Anxiety** (0.737) and **depression** (0.734)

**Main protective factors:**
- **Self-esteem** (-0.756)
- **Sleep quality** (-0.749)
- **Academic performance** (-0.721)

### 6. Modeling and Prediction

**Model for Dataset 1 (symptoms):**
- Accuracy: 96%
- Most important features: rapid heartbeat (0.1371), sleep problems (0.1114)

**Model for Dataset 2 (psychological indicators):**
- Most important features: blood pressure (0.1247), bullying (0.0870), sleep quality (0.0854)

### 7. Hypothesis Testing
- Hypothesis **"Academic workload is a key stress factor"** - **partially confirmed** (academic overload ranks 4th in importance)
- Hypothesis **"Sleep problems increase stress levels"** - **confirmed** (sleep quality is a key protective factor)
- Hypothesis **"Social support reduces distress levels"** - **confirmed** (social support has corr. -0.632)
- Hypothesis **"Eustress predominates over distress"** - **refuted** (distribution depends on data collection method)

## Key Conclusions and Recommendations

### Conclusions:
1. Bullying is the most destructive stress factor among students
2. Physiological markers (heart rate, blood pressure) are most significant for prediction
3. Sleep quality and self-esteem are key protective factors
4. Upper-year students are more susceptible to distress

### Recommendations:
1. **Priority:** Implement anti-bullying programs
2. **Develop** targeted support programs for upper-year students
3. **Focus** on strengthening self-esteem and improving sleep hygiene
4. **Reduce** academic overload
5. **Improve** student-teacher relationships
6. **Implement** monitoring of physiological indicators