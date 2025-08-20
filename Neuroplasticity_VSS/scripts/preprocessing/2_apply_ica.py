#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ICA Application Script for Visual Snow MEG Data
- Loads pre-computed ICA solution
- Applies component rejection to raw data
- Saves cleaned data and log file
"""

import os
import mne
from mne.preprocessing import read_ica

# ======================
# CONFIGURATION SETTINGS
# ======================
# Path configuration
BASE_PATH = '{path_to_data}'

# Subject and experiment info
SUBJECT = 'Subject_1'  # Change this for each subject
EXPERIMENT = 'gratings'
STIM_CHANNEL = 'STI101'

# ICA components to exclude (determined from visual inspection)
COMPONENTS_TO_EXCLUDE = {
    'ecg': [0],    # ECG artifacts
    'veog': [0], # Vertical EOG artifacts
    'heog': [0],     # Horizontal EOG artifacts
    'emg': [0],      # EMG artifacts
    'maxfilter': [0] # Maxfilter artifacts
}

# ======================
# MAIN PROCESSING
# ======================
def main():
    # Setup paths
    ica_dir = os.path.join(BASE_PATH, SUBJECT, 'ICA_notch')
    raw_file = os.path.join(ica_dir, f'{SUBJECT}_{EXPERIMENT}_raw.fif')
    ica_file = os.path.join(ica_dir, f'{SUBJECT}_{EXPERIMENT}_raw-ica.fif')
    output_file = os.path.join(ica_dir, f'{SUBJECT}_{EXPERIMENT}_ica-raw.fif')
    log_file = os.path.join(ica_dir, f'{SUBJECT}_{EXPERIMENT}_raw_ica_final.log')

    # Load raw data
    print(f"Loading raw data: {raw_file}")
    raw = mne.io.read_raw_fif(raw_file, preload=True)
    
    # Find events (for potential later use)
    events = mne.find_events(raw, stim_channel=STIM_CHANNEL, shortest_event=1)
    
    # Load ICA solution
    print(f"Loading ICA solution: {ica_file}")
    ica = read_ica(ica_file)
    
    # Combine all components to exclude
    exclude_components = []
    for component_type in COMPONENTS_TO_EXCLUDE.values():
        exclude_components.extend(component_type)
    
    # Apply ICA cleaning
    print(f"Applying ICA with excluded components: {exclude_components}")
    ica.apply(raw, exclude=exclude_components)
    
    # Save cleaned data
    print(f"Saving cleaned data to: {output_file}")
    raw.save(output_file, overwrite=True)
    
    # Save processing log
    save_processing_log(log_file, raw, COMPONENTS_TO_EXCLUDE)
    print("Processing complete")

def save_processing_log(log_file, raw, excluded_components):
    """Save information about the processing to a log file."""
    with open(log_file, 'w') as f:
        f.write(f'Sampling frequency: {raw.info["sfreq"]} Hz\n')
        f.write(f'ECG components excluded: {excluded_components["ecg"]}\n')
        f.write(f'Vertical EOG components excluded: {excluded_components["veog"]}\n')
        f.write(f'Horizontal EOG components excluded: {excluded_components["heog"]}\n')
        f.write(f'EMG components excluded: {excluded_components["emg"]}\n')
        f.write(f'Maxfilter components excluded: {excluded_components["maxfilter"]}\n')

if __name__ == '__main__':
    main()