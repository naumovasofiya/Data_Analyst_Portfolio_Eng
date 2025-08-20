# MEG Data Processing Pipeline

## 1. Preprocessing (`1_preprocessing_and_ica.py`)

### MaxFilter
- tSSS (temporal Signal Space Separation)
- Head movement compensation
- Bad channel interpolation

### ICA Artifact Removal
- Band-pass filtering (1-140 Hz)
- Notch filter (50 Hz and harmonics)
- Automatic detection:
  - ECG artifacts (max 3 components)
  - EOG artifacts (max 1 component per type)
- Visual inspection of components
- Result: Cleaned continuous data

### ICA Application (`2_apply_ica.py`)
- Manual component exclusion
- Saving cleaned continuous data

## 2. Epoching (`3_epoching_and_epochs_cleaning.py`)

### Epoch Creation
- 2-second epochs (50% overlap)
- Onset synchronized with every 7th reversal cycle (~150 ms intervals)

### Artifact Rejection
- Automatic:
  - Gradiometer threshold: 4000e-13 T/m
  - High-frequency gamma power exclusion (70-146 Hz, 2SD)
- Visual inspection
- Target: ~65 clean epochs per condition

## 3. Spectral Analysis (`4_psd_analysis.py`)

### Power Spectral Density
- Welch's method (3-s window: 2 s data + 0.5 s zero-padding)
- Frequency resolution: 0.33 Hz
- Target frequencies:
  - Fundamental: 6.666 Hz (F1)
  - Harmonics: 13.333 Hz (F2), 20.0 Hz (F3), 26.666 Hz (F4), 40.0 Hz (F6), 53.333 Hz (F8)

### Appelbaum, 2006 Metric
- Signal power: Sum at stimulation harmonics
- Background power: Average at adjacent frequencies (±0.333-0.666 Hz)

## 4. Contrast Response Function Modeling (`5_model_fitting.py`)

### Naka-Rushton Function

R = Rmax*C²/(v²ˢ + C²ˢ) + b

Where:
- R = Response power
- C = Stimulus contrast
- Rmax = Maximum response
- v = Semi-saturation constant
- s = Saturation exponent (key parameter)
- b = Baseline

### Model Fitting
- Nonlinear minimization (Lmfit)
- Parameter constraints:
  - v: 0-50
  - s: 0-5
  - b: ≥0

## 5. Statistical Analysis

### Group Comparisons
- Primary target: Saturation parameter (s)
- Tests: Student's t-test or Mann-Whitney U test
- Effect size: Cohen's d or r

### Parameter Correlation
- Spearman's rank correlation between visual discomfort score and saturation parameter

## Quality Control
- ICA component reports (HTML)
- Topographic maps for each harmonic
- Model fitting plots with R² values
- Component and epoch rejection statistics