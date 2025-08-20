"""
ICA Processing for MEG Data

This script performs Independent Component Analysis (ICA) on MEG data to identify and remove artifacts 
(ECG, EOG) from the recordings. It processes raw .fif files, applies filtering, runs ICA, 
and generates diagnostic plots and reports.

Key steps:
1. Load and preprocess raw MEG data
2. Perform ICA decomposition
3. Identify artifact components (ECG, EOG)
4. Generate quality control reports
5. Save cleaned data and ICA solution

"""

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import mne
from mne.preprocessing import ICA, create_ecg_epochs, create_eog_epochs
from mne.report import Report

# Close all existing plots
plt.close("all")

# ======================================================================
# CONFIGURATION PARAMETERS
# ======================================================================

# File paths
DATA_DIR = '{path_to_raw_data}'
OUTPUT_DIR = '{path_to_subjects_folders}/{subjects_folder}/{ICA}'

# Subject and experiment info
SUBJECTS = ['Subject_1']  # List of subject IDs
DATES = ['010101']    # Corresponding recording dates
EXPERIMENT = 'palinopsia'  # Experiment name

# Data rejection thresholds
MAG_REJECT = 4e-12      # Magnetometer rejection threshold (T)
GRAD_REJECT = 4000e-13  # Gradiometer rejection threshold (T/m)
reject = dict(mag=MAG_REJECT, grad=GRAD_REJECT)
flat = dict(mag=0.1e-12, grad=1e-13)

# Artifact channel configuration
ECG_CHANNEL = 'ECG063'  # ECG channel name
EOG_VERTICAL = True     # Whether to process vertical EOG
EOG_HORIZONTAL = True   # Whether to process horizontal EOG

# ICA parameters
NOTCH_FILTER = True     # Apply notch filter at 50Hz and harmonics
MAX_ECG_COMPONENTS = 3  # Max ECG components to reject
MAX_EOG_COMPONENTS = 3  # Max EOG components to reject

# ======================================================================
# MAIN PROCESSING PIPELINE
# ======================================================================

def process_subject(subject_id, recording_date):
    """Process MEG data for a single subject using ICA artifact removal."""
    
    # Set up file paths and directories
    ica_folder = 'ICA' if NOTCH_FILTER else 'ICA_nonotch'
    subject_dir = os.path.join(OUTPUT_DIR, subject_id)
    output_dir = os.path.join(subject_dir, ica_folder)
    
    # Create output directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize report for quality control
    report = Report()
    
    # ==================================================================
    # 1. DATA LOADING AND PREPROCESSING
    # ==================================================================
    
    print(f"\nProcessing subject: {subject_id}")
    
    # Find and load all raw files for this subject
    raw_files = sorted(glob.glob(
        os.path.join(DATA_DIR, subject_id, recording_date, 
                    f"{subject_id}_{EXPERIMENT}_run*_raw_tsss_mc_trans.fif")
    ))
    
    if not raw_files:
        raise FileNotFoundError(f"No raw files found for {subject_id}")
    
    # Load and preprocess each run
    raw_list = []
    for raw_file in raw_files:
        print(f"Loading file: {os.path.basename(raw_file)}")
        
        # Load raw data
        raw = mne.io.read_raw(raw_file, preload=True)
        
        # Apply basic filtering
        raw.filter(1, 140, n_jobs=1, fir_design='firwin')
        
        # Apply notch filter if specified
        if NOTCH_FILTER:
            raw.notch_filter(np.array([50, 100]))
        
        # Configure EOG channels
        if EOG_VERTICAL:
            raw.rename_channels({'EOG061': 'vEOG'})
            raw.set_channel_types({'vEOG': 'eog'})
        
        if EOG_HORIZONTAL:
            raw.rename_channels({'EOG062': 'hEOG'})
            raw.set_channel_types({'hEOG': 'eog'})
        
        # Crop data to relevant time period around events
        sfreq = raw.info['sfreq']
        events = mne.find_events(raw, stim_channel='STI101', verbose=True)
        
        # Select only relevant events (1-5)
        events = np.array([e for e in events if 1 <= e[2] <= 5])
        
        if len(events) > 0:
            start_time = events[0, 0]/sfreq - raw.first_samp/sfreq - 2.0
            end_time = events[-1, 0]/sfreq - raw.first_samp/sfreq + 2
            start_time = max(0, start_time)  # Ensure start isn't negative
            
            if subject_id != 'S035':  # Special case for one subject
                raw.crop(tmin=start_time, tmax=end_time)
        
        # Add raw to list for concatenation
        raw_list.append(raw)
    
    # Concatenate all runs
    raw_concat = mne.concatenate_raws(raw_list)
    del raw_list  # Free memory
    
    # Save concatenated raw file
    concat_filename = os.path.join(output_dir, f"{subject_id}_{EXPERIMENT}_raw.fif")
    raw_concat.save(concat_filename, overwrite=True)
    
    # Reload to ensure clean state
    raw_concat = mne.io.read_raw_fif(concat_filename, preload=True)
    
    # ==================================================================
    # 2. ICA DECOMPOSITION
    # ==================================================================
    
    print("\nRunning ICA decomposition...")
    
    # Select MEG channels for ICA
    ica_picks = mne.pick_types(raw_concat.info, meg=True, eeg=False, 
                              eog=False, stim=False, exclude='bads')
    
    # Determine data rank
    rank = mne.compute_rank(raw_concat, rank='info')['meg']
    
    # Run ICA
    ica = ICA(n_components=rank, method='fastica')
    ica.fit(raw_concat, picks=ica_picks, decim=4, 
            reject=reject, flat=flat, verbose=True)
    
    # Save ICA sources and solution
    ica_sources = ica.get_sources(raw_concat)
    ica_sources.save(
        os.path.join(output_dir, f"{subject_id}_{EXPERIMENT}_raw_ics_timecourse.fif"),
        overwrite=True
    )
    
    ica_filename = os.path.join(output_dir, f"{subject_id}_{EXPERIMENT}_raw-ica.fif")
    ica.save(ica_filename, overwrite=True)
    
    # ==================================================================
    # 3. ARTIFACT DETECTION AND REMOVAL
    # ==================================================================
    
    print("\nIdentifying artifact components...")
    
    # ECG artifact detection
    ecg_epochs = create_ecg_epochs(
        raw_concat, reject=reject, tmin=-.15, tmax=.4, 
        ch_name=None, l_freq=1.0, h_freq=20.0, picks=ica_picks
    )
    
    ecg_components, ecg_scores = ica.find_bads_ecg(
        ecg_epochs, threshold=0.4, method='ctps'
    )
    
    # Add ECG results to report
    report.add_figure(
        ica.plot_scores(ecg_scores, exclude=ecg_components, 
                        title='ECG artifact scores'),
        title='ECG component scores',
        section='Artifact Detection'
    )
    
    if ecg_components:
        ecg_components = ecg_components[:MAX_ECG_COMPONENTS]
        ica.exclude += ecg_components
        
        # Add ECG component plots
        report.add_figure(
            ica.plot_components(ecg_components, ch_type='mag', 
                               title='ECG components (magnetometers)'),
            title='ECG components (mag)',
            section='Artifact Detection'
        )
        report.add_figure(
            ica.plot_components(ecg_components, ch_type='grad', 
                               title='ECG components (gradiometers)'),
            title='ECG components (grad)',
            section='Artifact Detection'
        )
        
        # Add ECG source and overlay plots
        ecg_evoked = ecg_epochs.average()
        report.add_figure(
            ica.plot_sources(ecg_evoked),
            title='ECG component time courses',
            section='Artifact Detection'
        )
        report.add_figure(
            ica.plot_overlay(ecg_evoked),
            title='ECG artifact removal',
            section='Artifact Detection'
        )
    
    # Vertical EOG artifact detection
    if EOG_VERTICAL:
        veog_components, veog_scores = ica.find_bads_eog(
            raw_concat, ch_name='vEOG'
        )
        
        if veog_components:
            veog_components = veog_components[:MAX_EOG_COMPONENTS]
            ica.exclude += veog_components
            
            # Add vEOG results to report
            report.add_figure(
                ica.plot_scores(veog_scores, exclude=veog_components, 
                               title='vEOG artifact scores'),
                title='vEOG component scores',
                section='Artifact Detection'
            )
            report.add_figure(
                ica.plot_components(veog_components, ch_type='mag', 
                                   title='vEOG components (magnetometers)'),
                title='vEOG components (mag)',
                section='Artifact Detection'
            )
            
            # Try to create and plot vEOG epochs
            try:
                veog_evoked = create_eog_epochs(
                    raw_concat, reject=reject, flat=flat,
                    ch_name='vEOG', tmin=-.5, tmax=.5, 
                    picks=ica_picks
                ).average()
                
                report.add_figure(
                    ica.plot_sources(veog_evoked, exclude=veog_components),
                    title='vEOG component time courses',
                    section='Artifact Detection'
                )
                report.add_figure(
                    ica.plot_overlay(veog_evoked, exclude=veog_components),
                    title='vEOG artifact removal',
                    section='Artifact Detection'
                )
            except ValueError as e:
                print(f"Could not create vEOG epochs: {str(e)}")
    
    # Horizontal EOG artifact detection
    if EOG_HORIZONTAL:
        heog_components, heog_scores = ica.find_bads_eog(
            raw_concat, ch_name='hEOG'
        )
        
        if heog_components:
            heog_components = heog_components[:MAX_EOG_COMPONENTS]
            ica.exclude += heog_components
            
            # Add hEOG results to report
            report.add_figure(
                ica.plot_scores(heog_scores, exclude=heog_components, 
                               title='hEOG artifact scores'),
                title='hEOG component scores',
                section='Artifact Detection'
            )
            report.add_figure(
                ica.plot_components(heog_components, ch_type='grad', 
                                   title='hEOG components (gradiometers)'),
                title='hEOG components (grad)',
                section='Artifact Detection'
            )
            
            # Try to create and plot hEOG epochs
            try:
                heog_evoked = create_eog_epochs(
                    raw_concat, reject=reject, flat=flat,
                    ch_name='hEOG', tmin=-.5, tmax=.5, 
                    picks=ica_picks
                ).average()
                
                report.add_figure(
                    ica.plot_sources(heog_evoked, exclude=heog_components),
                    title='hEOG component time courses',
                    section='Artifact Detection'
                )
                report.add_figure(
                    ica.plot_overlay(heog_evoked, exclude=heog_components),
                    title='hEOG artifact removal',
                    section='Artifact Detection'
                )
            except ValueError as e:
                print(f"Could not create hEOG epochs: {str(e)}")
    
    # ==================================================================
    # 4. QUALITY CONTROL AND REPORTING
    # ==================================================================
    
    print("\nGenerating quality control report...")
    
    # Plot all ICA components in groups of 20
    all_components = np.arange(rank)
    component_groups = [
        all_components[i:i+20] for i in range(0, len(all_components), 20)
    ]
    
    for i, group in enumerate(component_groups):
        fig = ica.plot_components(group)
        report.add_figure(
            fig,
            title=f'ICA components {group[0]}-{group[-1]}',
            section='ICA Components'
        )
    
    # Plot PSD for magnetometers and gradiometers
    for ch_type in ['mag', 'grad']:
        picks = mne.pick_types(raw_concat.info, meg=ch_type)
        fig = raw_concat.plot_psd(
            tmin=0.0, tmax=None, fmin=1, fmax=140, 
            picks=picks, area_mode='std', show=False
        )
        report.add_figure(
            fig,
            title=f'Power spectrum ({ch_type})',
            section='Power Spectra'
        )
    
    # Save processing log
    log_filename = os.path.join(output_dir, f"{subject_id}_{EXPERIMENT}_raw_ica.log")
    with open(log_filename, 'w') as f:
        f.write(f"Data rank after SSS: {rank}\n")
        f.write(f"Sampling frequency: {raw_concat.info['sfreq']} Hz\n")
        f.write(f"ECG components excluded: {ecg_components}\n")
        f.write(f"vEOG components excluded: {veog_components if EOG_VERTICAL else 'N/A'}\n")
        f.write(f"hEOG components excluded: {heog_components if EOG_HORIZONTAL else 'N/A'}\n")
    
    # Save final report
    report_filename = os.path.join(output_dir, f"{subject_id}_{EXPERIMENT}_raw-ica.html")
    report.save(report_filename, open_browser=False, overwrite=True)
    
    print(f"\nProcessing complete for {subject_id}")
    print(f"Report saved to: {report_filename}")

# ======================================================================
# RUN PROCESSING FOR ALL SUBJECTS
# ======================================================================

if __name__ == "__main__":
    for subject, date in zip(SUBJECTS, DATES):
        process_subject(subject, date)