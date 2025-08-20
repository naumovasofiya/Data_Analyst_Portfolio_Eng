# Investigation of Neuroplasticity in the Visual Cortex in Visual Snow Syndrome Using Magnetoencephalography

[Presentation of Results](https://github.com/naumovasofiya/MEG-Analysis-of-Neuroplasticity-in-VSS/blob/533bf675c34520fe9e4a6744f912ae1adf3a8ee0/Neuroplasticity_VSS/results/figures_and_presentation/Naumova_presentation.pdf)

## Research Objective
To study the excitation-inhibition balance (E-I balance) and mechanisms of neuroplasticity in the visual cortex of patients with Visual Snow Syndrome (VSS) through the analysis of gamma oscillation dynamics (30-100 Hz) during repetitive visual stimulation.

## Research Tasks
1. Compare the parameters of gamma responses (GR) to stimuli with different movement speeds between patients with VSS and a control group.
2. Investigate the dynamics of changes in GR power and frequency.
3. Assess the relationship between GR dynamics and the severity of VSS symptoms.
4. Test the hypotheses about:
   - Impaired E-I balance in the visual cortex in VSS.
   - Abnormal neuroplasticity as the basis of VSS pathogenesis.

## Methods and Materials
### Participants:
- **VSS group**: 26 patients (14 male, age 18-37 years, M=26.7)
- **Control group**: 27 healthy individuals (16 male, age 18-37 years, M=26.9)

### Stimulation Paradigm:
- Circular gratings (100% contrast, 1.66 cycles/degree)
- 5 conditions: static (0°/s) and moving (0.6, 1.2, 3.6, 6.0°/s)
- 90 presentations per condition (450 presentations total), duration 1.2-1.6 s

### Equipment:
- MEG system "Elekta Neuromag" (306 channels)
- Software:
  - MaxFilter 2.2 (tSSS correction)
  - MNE-Python 1.7.1 (analysis)
  - Python 3.10 / R 4.3.1 (statistics)

### Data Analysis:
1. **Preprocessing**:
   - Filtering 0.1-330 Hz + 50 Hz notch
   - ICA artifact correction
   - Epochs: -1.0 to +1.2 s relative to stimulus

2. **GR Analysis**:
   - Time-frequency analysis (multitaper)
   - Normalization: (stimulus - baseline)/baseline × 100%
   - Key metrics:
     - Peak GR power (35-100 Hz)
     - GR spectral centroid

3. **Statistics**:
   - Mixed ANOVA (Group × Condition)
   - Linear mixed models for analyzing individual presentations
   - Spearman correlation

## Key Results
### 1. Behavioral Data:
- **Errors**:
  - Commission errors: VSS 3.54% vs control 1.81% (p=0.006)
  - Omission errors: no group differences (p=0.42)
- **Reaction Time**:
  - Dependent on movement speed (p<0.001)
  - No group differences (p=0.73)

### 2. Gamma Responses:
- **Mean GR Power**:
  - Inverted U-dependence on movement speed (peak at 1.2°/s)
  - No group differences (p=0.2)
- **GR Frequency**:
  - Monotonic increase with increasing movement speed
  - No group differences (p=0.38)

### 3. Single-Trial Analysis:
- **Biphasic GR Power Dynamics**:
  - Rapid decrease (τ≈7.8 repetitions) → linear increase
  - More pronounced increase in VSS (β=0.246 vs 0.167, p=0.03)
- **GR Frequency**:
  - Moderate increase with repetition (p=0.015)
  - No group differences (p=0.23)

### 4. Clinical Correlations:
- **Visual Discomfort Scale**:
  - Higher in VSS (p<0.001)
  - No correlation with GR dynamics (R=0.027, p=0.9)
- **Anxiety (STAI)**:
  - Higher in VSS (p<0.001)

## Conclusions
1. **Preserved Excitation-Inhibition Balance**:
   - VSS patients show preserved normal patterns of GR modulation by movement speed.
   - Absence of abnormalities in GR frequency.

2. **Enhanced Neuroplasticity**:
   - Greater increase in GR power with repeated presentations compared to the control group.
   - Consistent with a model of enhanced Hebbian plasticity.

3. **Applied Significance**:
   - GR dynamics are a potential biomarker for plasticity in VSS.
   - Potential treatment methods aimed at modulating plasticity may be effective for VSS.

## Future Directions
1. Investigation of VSS subgroups (comorbid conditions).
2. Source-level analysis of brain activity for precise localization of effects.
3. Longitudinal studies on the relationship between GR dynamics and symptom progression.