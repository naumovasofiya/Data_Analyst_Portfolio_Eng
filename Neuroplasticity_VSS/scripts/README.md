# MEG Data Processing Pipeline for Visual Snow Syndrome (VSS) Study

## Overview
This repository contains scripts for processing MEG data from a visual snow syndrome gratings experiment. The pipeline includes:
1. ICA artifact removal and data cleaning
2. Epoching and trial rejection
3. Time-frequency analysis (gamma-band)
4. Behavioral response time analysis
5. Experimental variable enhancement
6. Statistical analysis of gamma dynamics

## Scripts

### 1. Preprocessing Pipeline
- `1_preprocessing_and_ica.py`: Performs ICA decomposition and artifact detection (ECG/EOG) on raw MEG data
- `2_apply_ica.py`: Applies ICA corrections to remove artifacts from raw data
- `3_epoching_and_epoch_cleaning.py`: Creates epochs from cleaned data and performs manual trial rejection via visual inspection

### 2. Core Analysis Scripts
- `4_analyze_gamma_power.py`: Computes gamma-band power and frequency features, performs group comparisons
- `process_reaction_times.py`: Processes behavioral response data from experiment log files
- `enhance_behavioral_data.py`: Adds experimental variables (block info, timing between stimuli) to behavioral data
- `analyze_vss_gamma_dynamics.R`: R script for statistical analysis and visualization of gamma dynamics (power changes, frequency shifts)

### 3. Output Files
- Processed MEG data: `{path_to_original_data}`
- Analysis results: `{path_to_data}`
- Includes: cleaned epochs, time-frequency results, response time data, gamma power statistics

## Requirements
### Python
- Python 3.x with:
  - MNE-Python (v1.0+ recommended)
  - NumPy
  - Pandas
  - Matplotlib
  - Scipy

### R
- R (for statistical analysis) with:
  - ggplot2
  - dplyr
  - nlme
  - segmented
  - tidyr
  - purrr

## Usage Instructions
1. Run preprocessing steps in sequence:
   `1_preprocessing_and_ica.py` → `2_apply_ica.py` → `3_epoching_and_epoch_cleaning.py`
2. Run analysis scripts as needed:
   - For gamma analysis: `4_analyze_gamma_power.py`
   - For behavioral analysis: `process_reaction_times.py` followed by `enhance_behavioral_data.py`
   - For statistical modeling: `analyze_vss_gamma_dynamics.R`
3. Check individual script headers for subject lists and exact paths before running

## Notes
- **Subject IDs**: 
  - Healthy controls start with 'X0' (e.g., S001-S039)
  - VSS patients start with 'X1' or 'X2'
- **Special handling**: Subjects XXX and YYY are excluded from response time analysis
- **Path configuration**: Scripts assume specific server paths - modify `DATA_PATH` and `OUTPUT_PATH` variables as needed for your setup
- **Hardware delay**: 50ms delay compensation applied uniformly across processing
- **Gamma range**: Analyzed at 30-100 Hz with baseline correction (-0.9 to 0s)