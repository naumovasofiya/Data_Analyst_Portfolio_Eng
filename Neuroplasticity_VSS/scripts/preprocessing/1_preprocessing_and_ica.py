#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ICA Processing for Visual Snow MEG Data
- Reads and concatenates raw .fif files
- Runs ICA on concatenated data
- Identifies and removes artifact components (ECG/EOG)
- Saves cleaned data and reports
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt
import mne
from mne import io
from mne.preprocessing import ICA, create_ecg_epochs, create_eog_epochs
from mne.report import Report

# Close any existing plots
plt.close("all")

# ======================
# CONFIGURATION SETTINGS
# ======================
SUBJECTS = ['Subject_1']
DATES = ['010101']
EXPERIMENT = 'gratings'
STIM_CHANNEL = 'STI101'

# Path configuration
BASE_DATA_PATH = '{path_to_original_data}'
OUTPUT_PATH = '{path_to_data}'

# Rejection thresholds (adult values)
REJECT_THRESHOLDS = dict(mag=8e-12, grad=8000e-13)
FLAT_THRESHOLDS = dict(mag=0.1e-12, grad=1e-13)

# Artifact detection settings
MAX_ECG_COMPONENTS = 3  # Maximum ECG components to reject
MAX_EOG_COMPONENTS = 1  # Maximum EOG components to reject

# Channel configuration
ECG_CHANNEL = 'ECG063'
EOG_CHANNELS = {
    'vertical': {'enabled': True, 'ch1': 'EOG061', 'ch2': None},
    'horizontal': {'enabled': True, 'ch1': 'EOG062', 'ch2': None}
}

# Processing flags
APPLY_NOTCH_FILTER = True  # Set to False to skip notch filtering

# ======================
# MAIN PROCESSING LOOP
# ======================
for subj_idx, subject in enumerate(SUBJECTS):
    start_time = time.time()
    
    # Setup paths and folders
    notch_suffix = '_notch' if APPLY_NOTCH_FILTER else ''
    ica_folder = f'ICA{"_notch" if APPLY_NOTCH_FILTER else "_nonotch"}'
    
    # Create output directories
    os.makedirs(os.path.join(OUTPUT_PATH, subject, ica_folder), exist_ok=True)
    save_path = os.path.join(OUTPUT_PATH, subject, ica_folder)
    
    # Setup logging
    log_file = os.path.join(save_path, f'{subject}_{EXPERIMENT}_ICA_stdout.txt')
    mne.set_log_file(log_file, output_format='%(message)s', overwrite=True)
    
    # ======================
    # DATA LOADING
    # ======================
    raw_files = []
    report = Report()
    data_path = os.path.join(BASE_DATA_PATH, subject, DATES[subj_idx])
    
    # Load and process each run
    for run in [1, 2]:  # Only run1 and run2
        raw_fname = f'{subject}_{EXPERIMENT}_run{run}_raw_tsss_mc_trans.fif'
        print(f"Processing: {raw_fname}")
        
        # Load raw data
        raw = io.Raw(os.path.join(data_path, raw_fname), preload=True)
        
        # Apply notch filter if enabled
        if APPLY_NOTCH_FILTER:
            print("Applying notch filter...")
            raw.notch_filter(np.arange(50, 240, 50))
        
        # Configure EOG channels
        if EOG_CHANNELS['vertical']['enabled']:
            raw.rename_channels({EOG_CHANNELS['vertical']['ch1']: 'vEOG'})
            raw.set_channel_types({'vEOG': 'eog'})
        
        if EOG_CHANNELS['horizontal']['enabled']:
            raw.rename_channels({EOG_CHANNELS['horizontal']['ch1']: 'hEOG'})
            raw.set_channel_types({'hEOG': 'eog'})
        
        # Add raw to list for concatenation
        raw_files.append(raw)
        
        # Create diagnostic plots
        create_diagnostic_plots(raw, report, subject, run, REJECT_THRESHOLDS)
    
    # Concatenate all runs
    combined_raw = mne.concatenate_raws(raw_files)
    combined_raw.save(os.path.join(save_path, f'{subject}_{EXPERIMENT}_raw.fif'), overwrite=True)
    
    # ======================
    # ICA PROCESSING
    # ======================
    # Select channels for ICA (MEG only)
    ica_picks = mne.pick_types(combined_raw.info, meg=True, eeg=False, eog=False, stim=False, exclude='bads')
    
    # Run ICA
    ica = ICA(n_components=80, method='fastica')
    ica.fit(combined_raw, picks=ica_picks, decim=4, reject=REJECT_THRESHOLDS, flat=FLAT_THRESHOLDS)
    
    # Save ICA components
    ica_sources = ica.get_sources(combined_raw)
    ica_sources.save(os.path.join(save_path, f'{subject}_{EXPERIMENT}_raw_ics_timecourse.fif'))
    ica.save(os.path.join(save_path, f'{subject}_{EXPERIMENT}_raw-ica.fif'))
    
    # ======================
    # ARTIFACT DETECTION
    # ======================
    # ECG artifact detection
    ecg_components = detect_ecg_artifacts(ica, combined_raw, report, subject)
    
    # EOG artifact detection
    eog_components = detect_eog_artifacts(ica, combined_raw, report, subject, 
                                         EOG_CHANNELS['vertical']['enabled'], 
                                         EOG_CHANNELS['horizontal']['enabled'])
    
    # ======================
    # SAVE RESULTS
    # ======================
    # Save log file
    with open(os.path.join(save_path, f'{subject}_{EXPERIMENT}_raw_ica.log'), 'w') as f:
        f.write(f'Data rank after SSS: 80\n')
        f.write(f'Sampling freq: {combined_raw.info["sfreq"]}\n')
        f.write(f'ECG exclude {ecg_components}\n')
        f.write(f'vEOG exclude {eog_components.get("vertical", [])}\n')
        f.write(f'hEOG exclude {eog_components.get("horizontal", [])}\n')
    
    # Save HTML report
    report.save(os.path.join(save_path, f'{subject}_{EXPERIMENT}_raw-ica.html'), overwrite=True)
    
    print(f"Completed processing for {subject} in {time.time()-start_time:.1f} seconds")

# ======================
# HELPER FUNCTIONS
# ======================
def create_diagnostic_plots(raw, report, subject, run, reject_thresholds):
    """Create and save diagnostic plots for raw data."""
    # Create sample points for plotting (every 10th point to reduce memory)
    sample_points = np.arange(0, raw._data.shape[1], 10)
    
    # Plot gradiometers
    fig1 = plt.figure(figsize=(15, 5))
    for ch in np.arange(1, 303, 3):
        plt.plot(raw._data[ch, sample_points])
    plt.title('Gradiometers')
    plt.ylabel('Signal amplitude (T/m)')
    plt.axis([0, len(sample_points), -reject_thresholds['grad'], reject_thresholds['grad']])
    report.add_figs_to_section(fig1, f'RAW signal run{run} gradiometers', f'RAW {subject}')
    
    # Plot magnetometers
    fig2 = plt.figure(figsize=(15, 5))
    for ch in np.arange(2, 303, 3):
        plt.plot(raw._data[ch, sample_points])
    plt.title('Magnetometers')
    plt.ylabel('Signal amplitude (T)')
    plt.axis([0, len(sample_points), -reject_thresholds['mag'], reject_thresholds['mag']])
    report.add_figs_to_section(fig2, f'RAW signal run{run} magnetometers', f'RAW {subject}')
    
    plt.close('all')

def detect_ecg_artifacts(ica, raw, report, subject):
    """Detect and mark ECG artifacts in ICA components."""
    ecg_epochs = create_ecg_epochs(raw, tmin=-0.5, tmax=0.5)
    ecg_components, scores = ica.find_bads_ecg(ecg_epochs, method='ctps')
    
    if ecg_components:
        # Add to report
        fig1 = ica.plot_scores(scores, exclude=ecg_components, title='ECG components')
        fig2 = ica.plot_components(ecg_components, title='ECG components', colorbar=True)
        report.add_figs_to_section([fig1, fig2], 'ECG artifact detection', f'Artifacts {subject}')
        
        # Limit number of components to reject
        ecg_components = ecg_components[:MAX_ECG_COMPONENTS]
        ica.exclude.extend(ecg_components)
    
    return ecg_components

def detect_eog_artifacts(ica, raw, report, subject, detect_vertical=True, detect_horizontal=True):
    """Detect and mark EOG artifacts in ICA components."""
    eog_components = {}
    
    if detect_vertical:
        eog_epochs = create_eog_epochs(raw, ch_name='vEOG')
        veog_components, scores = ica.find_bads_eog(eog_epochs)
        
        if veog_components:
            fig = ica.plot_scores(scores, exclude=veog_components)
            report.add_figs_to_section([fig], 'vEOG artifact detection', f'Artifacts {subject}')
            veog_components = veog_components[:MAX_EOG_COMPONENTS]
            ica.exclude.extend(veog_components)
            eog_components['vertical'] = veog_components
    
    if detect_horizontal:
        eog_epochs = create_eog_epochs(raw, ch_name='hEOG')
        heog_components, scores = ica.find_bads_eog(eog_epochs)
        
        if heog_components:
            fig = ica.plot_scores(scores, exclude=heog_components)
            report.add_figs_to_section([fig], 'hEOG artifact detection', f'Artifacts {subject}')
            heog_components = heog_components[:MAX_EOG_COMPONENTS]
            ica.exclude.extend(heog_components)
            eog_components['horizontal'] = heog_components
    
    return eog_components