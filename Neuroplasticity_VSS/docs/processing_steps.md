# MEG Processing Pipeline for Visual Snow Syndrome Study

## 1. Preprocessing

### 1.1 ICA Artifact Removal (`1_preprocessing_and_ica.py`)
- **Raw data concatenation** across runs
- **Notch filtering** (50Hz + harmonics, optional)
- **Automatic artifact detection**:
  - ECG artifacts (max 3 components)
  - Vertical/Horizontal EOG artifacts (max 1 component each)
- **Output**: Saves ICA components and timecourses

### 1.2 Apply ICA (`2_apply_ica.py`)
- **Manual component rejection** based on:
  - ECG patterns
  - EOG patterns
  - EMG artifacts
  - MaxFilter artifacts
- **Output**: Saves cleaned continuous data

## 2. Epoching and Cleaning

### 2.1 Epoch Creation (`3_epoching_and_epoch_cleaning.py`)
- **Time windows**:
  - Baseline: -1.0 to 0s
  - Post-stim: 0 to 1.2s
- **50ms hardware delay compensation**
- **Event IDs**: V0 (static) to V4 (6.0°/s)
- **Artifact rejection**:
  - Gradiometers: 4000e-13 threshold

### 2.2 Manual Cleaning
- Visual inspection of epochs
- Trial-by-trial rejection

## 3. Gamma Band Analysis

### 3.1 Time-Frequency Decomposition (`4_analyze_gamma_power.py`)
- **Frequency range**: 5-120Hz (focus on 30-100 Hz gamma)
- **Method**: Multitaper (time-bandwidth=10.0)
- **Baseline normalization**: -0.9 to 0s
- **Top channel selection** based on gamma power

### 3.2 Single-Trial Features
- Gamma power extraction
- Peak frequency detection (Gaussian fitting)
- Response window: 0.3-1.2s post-stimulus

## 4. Behavioral Analysis

### 4.1 Response Processing (`process_reaction_times.py`)
- **Response classification**:
  - 0: Correct
  - 1: Late but within extended window
  - 2: Very late/missed
- Matches responses with MEG epochs

### 4.2 Experimental Variables (`enhance_behavioral_data.py`)
- Block information (3 blocks per session)
- Timing between stimuli
- Stimulus repetition counts

## 5. Statistical Analysis (`analyze_vss_gamma_dynamics.R`)

### Analysis Components:
- Group comparisons (VSS vs controls)
- Non-linear modeling of power changes
- Block-wise analysis

### Visualization:
- Gamma power dynamics
- Frequency shifts
- Condition-specific effects

