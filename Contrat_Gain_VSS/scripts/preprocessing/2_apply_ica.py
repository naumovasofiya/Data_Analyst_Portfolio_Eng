"""
ICA Application Script

This script applies previously computed ICA components to remove artifacts from MEG data.
It loads the raw data and ICA solution, excludes specified components, and saves the cleaned data.

Key steps:
1. Load raw data and ICA solution
2. Specify components to exclude (ECG, EOG, EMG artifacts)
3. Apply ICA cleaning
4. Save cleaned data and processing log

"""

import os
import glob
import mne
from mne.preprocessing import read_ica

# ======================================================================
# CONFIGURATION PARAMETERS
# ======================================================================

# Subject and experiment info
SUBJECT_ID = 'Subject_1'
EXPERIMENT = 'palinopsia'

# File paths
INPUT_DIR = '{path_to_subjects_folders}/{subjects_folder}/{ICA}'
OUTPUT_DIR = INPUT_DIR  # Same directory for input/output in this case

# Components to exclude (determined from visual inspection)
ECG_COMPONENTS = [0]    # ECG artifact components
VEOG_COMPONENTS = [0]    # Vertical EOG components
HEOG_COMPONENTS = [0]      # Horizontal EOG components
EMG_COMPONENTS = [0]       # EMG artifact components
MAXFILTER_COMPONENTS = [0] # Components related to MaxFilter artifacts

# ======================================================================
# MAIN PROCESSING FUNCTION
# ======================================================================

def apply_ica_cleaning():
    """Apply ICA cleaning to MEG data and save results."""
    
    # Close all existing plots
    plt.close("all")
    
    # Find input raw file
    raw_files = glob.glob(os.path.join(INPUT_DIR, f'*{EXPERIMENT}_raw.fif'))
    if not raw_files:
        raise FileNotFoundError(f"No raw files found for {SUBJECT_ID}")
    
    raw_file = raw_files[0]
    print(f"Loading raw data from: {raw_file}")
    
    # Load raw data
    raw = mne.io.read_raw_fif(raw_file, allow_maxshield=True, preload=True)
    
    # Load ICA solution
    ica_file = os.path.join(INPUT_DIR, f'{SUBJECT_ID}_{EXPERIMENT}_raw-ica.fif')
    ica = read_ica(ica_file)
    
    # Combine all components to exclude
    exclude_components = (
        ECG_COMPONENTS + 
        VEOG_COMPONENTS + 
        HEOG_COMPONENTS + 
        EMG_COMPONENTS + 
        MAXFILTER_COMPONENTS
    )
    
    print(f"\nExcluding components: {exclude_components}")
    
    # Apply ICA cleaning
    ica.apply(raw, exclude=exclude_components)
    
    # Save cleaned data
    output_file = os.path.join(OUTPUT_DIR, f'{SUBJECT_ID}_{EXPERIMENT}_icapy3-raw.fif')
    raw.save(output_file, overwrite=True)
    print(f"\nSaved cleaned data to: {output_file}")
    
    # Save processing log
    save_processing_log(raw, exclude_components)
    
    # Optional: Plot cleaned data
    # raw.plot(n_channels=102, block=True)

def save_processing_log(raw_data, excluded_components):
    """Save information about the processing to a log file."""
    log_file = os.path.join(
        OUTPUT_DIR, 
        f'{SUBJECT_ID}_{EXPERIMENT}_raw_ica_final.log'
    )
    
    log_content = f"""Processing log for ICA application
=================================
Sampling frequency: {raw_data.info['sfreq']} Hz
ECG components excluded: {ECG_COMPONENTS}
Vertical EOG components excluded: {VEOG_COMPONENTS}
Horizontal EOG components excluded: {HEOG_COMPONENTS}
EMG components excluded: {EMG_COMPONENTS}
MaxFilter components excluded: {MAXFILTER_COMPONENTS}
Total components excluded: {len(excluded_components)}
"""
    
    with open(log_file, 'w') as f:
        f.write(log_content)
    
    print(f"Saved processing log to: {log_file}")

# ======================================================================
# RUN PROCESSING
# ======================================================================

if __name__ == "__main__":
    apply_ica_cleaning()