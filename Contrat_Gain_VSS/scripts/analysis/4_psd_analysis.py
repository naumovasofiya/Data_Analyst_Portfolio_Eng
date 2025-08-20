"""
MEG Power Spectral Density (PSD) Analysis Pipeline

This script performs:
1. PSD calculation for different contrast conditions
2. Topographic mapping of frequency bands
3. Appelbaum metric calculation
4. Generation of interactive HTML reports

"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne
from mne import Report

# ======================================================================
# CONFIGURATION PARAMETERS
# ======================================================================

# Subject and group info
GROUP = 'VS'
SUBJECTS = ['Subject_1']  # List of subject IDs

# File paths
BASE_DIR = '{path_to_subjects_folders}/{subjects_folder}/{ICA}'
ICA_FOLDER = 'ICA'

# Analysis parameters
FREQ_BANDS = [  # Frequency bands of interest (Hz)
    (6.666, 'F1'), (13.333, 'F2'), (20.0, 'F3'),
    (26.666, 'F4'), (40.0, 'F6'), (53.333, 'F8')
]
FREQ_INDICES = [17, 37, 57, 77, 117, 157]  # Corresponding frequency indices
N_MAX_SENSORS = 1  # Number of top sensors to consider

# PSD calculation parameters
PSD_PARAMS = {
    'method': 'welch',
    'fmin': 1,
    'fmax': 60,
    'n_fft': 3000,
    'n_per_seg': 2000
}

# ======================================================================
# PROCESSING FUNCTIONS
# ======================================================================

def load_epochs(subject):
    """Load cleaned epochs for a subject."""
    epochs_file = os.path.join(
        BASE_DIR, GROUP, subject, ICA_FOLDER,
        f"{subject}-clean-epo.fif"
    )
    return mne.read_epochs(epochs_file).pick('grad')

def calculate_psd(epochs):
    """Calculate PSD for each condition."""
    psd_data = []
    psd_dfs = []
    
    for condition in ['C1', 'C2', 'C3', 'C4', 'C5']:
        evoked = epochs[condition].average()
        psd = evoked.compute_psd(**PSD_PARAMS)
        psd_df = psd.to_data_frame()
        
        psd_data.append(psd)
        psd_dfs.append(psd_df)
    
    # Process PSD dataframes
    freqs = psd_dfs[0]['freq']
    psd_arrays = [df.drop(columns='freq').T for df in psd_dfs]
    
    # Calculate average of C4 and C5 conditions
    h45 = (psd_arrays[3] + psd_arrays[4]) / 2
    
    return freqs, psd_arrays, h45

def create_individual_report(subject, freqs, psd_arrays, h45, epochs):
    """Generate HTML report for a single subject."""
    report = Report(title=f'Photo driving in {subject}')
    
    # 1. Create topomap of average power
    avg_power = np.mean(h45.iloc[:, FREQ_INDICES], axis=1)
    fig, ax = plt.subplots()
    mne.viz.plot_topomap(avg_power, epochs.info, axes=ax)
    plt.colorbar(ax=ax, shrink=0.75, label='Average power')
    report.add_figure(
        fig,
        title=f'{subject} Average Power',
        caption='Average power across harmonics',
        image_format='PNG'
    )
    
    # 2. Plot PSD for top sensors
    top_sensors = np.argpartition(avg_power, -N_MAX_SENSORS)[-N_MAX_SENSORS:]
    fig = plt.figure(figsize=(18, 6))
    
    for i, condition in enumerate(['C1', 'C2', 'C3', 'C4', 'C5']):
        plt.plot(
            freqs,
            psd_arrays[i].iloc[top_sensors, :].mean(axis=0),
            label=condition
        )
    
    # Add frequency band markers
    for freq, label in FREQ_BANDS:
        plt.axvline(x=freq, color='k', linestyle='dashed', label=label)
    
    plt.legend()
    report.add_figure(
        fig,
        title='Power Spectra',
        caption=f'Average PSD for top {N_MAX_SENSORS} sensors',
        image_format='PNG'
    )
    
    # 3. Create topomaps for each frequency band and condition
    container = epochs['C5'][0].pick('grad')
    for condition in ['C1', 'C2', 'C3', 'C4', 'C5']:
        evoked = epochs[condition].average()
        container._data[0, :, :] = evoked._data
        fig = container.plot_psd_topomap(
            bands=FREQ_BANDS,
            normalize=True,
            bandwidth=0.5
        )
        report.add_figure(
            fig,
            title=f'Topomap - {condition}',
            caption=f'Normalized power for {condition}',
            image_format='PNG'
        )
    
    # Save report
    report_file = os.path.join(
        BASE_DIR, GROUP, subject, ICA_FOLDER,
        f'report_Nmax_{N_MAX_SENSORS}_{subject}.html'
    )
    report.save(report_file, overwrite=True)
    plt.close('all')
    
    return avg_power

def calculate_appelbaum_metric(psd_arrays, freqs, top_sensors):
    """Calculate Appelbaum metric for each condition."""
    appelbaum = []
    baseline_matrix = np.zeros((5, len(FREQ_INDICES)))  # contrasts x harmonics
    
    for i in range(5):  # For each condition
        # Calculate signal power (sum across harmonics)
        signal_power = np.sqrt(
            psd_arrays[i].iloc[top_sensors, FREQ_INDICES].mean(axis=0).sum())
        
        # Calculate baseline power (average of surrounding frequencies)
        for n, j in enumerate(FREQ_INDICES):
            baseline_indices = [j-3, j-2, j+2, j+3]
            baseline_matrix[i, n] = psd_arrays[i].iloc[top_sensors, baseline_indices].mean()
        
        appelbaum.append(signal_power)
    
    # Calculate overall baseline
    baseline = np.sqrt(baseline_matrix.mean(axis=0).sum())
    
    return [baseline] + appelbaum

# ======================================================================
# MAIN PROCESSING PIPELINE
# ======================================================================

def process_subject(subject):
    """Run complete PSD analysis for one subject."""
    print(f"\nProcessing subject: {subject}")
    
    try:
        # Load data
        epochs = load_epochs(subject)
        
        # Calculate PSD
        freqs, psd_arrays, h45 = calculate_psd(epochs)
        
        # Create individual report and get average power
        avg_power = create_individual_report(subject, freqs, psd_arrays, h45, epochs)
        
        # Calculate Appelbaum metric
        top_sensors = np.argpartition(avg_power, -N_MAX_SENSORS)[-N_MAX_SENSORS:]
        appelbaum = calculate_appelbaum_metric(psd_arrays, freqs, top_sensors)
        
        print(f"Completed processing for {subject}")
        return appelbaum
    
    except Exception as e:
        print(f"Error processing {subject}: {str(e)}")
        return None

def create_group_report(group_avg_power, epochs_info):
    """Create HTML report for group average."""
    report = Report(title=f'Photo driving for {GROUP} group')
    
    fig, ax = plt.subplots()
    mne.viz.plot_topomap(group_avg_power, epochs_info, axes=ax)
    plt.colorbar(ax=ax, shrink=0.75, label='Average power')
    report.add_figure(
        fig,
        title=f'Group Average - {GROUP}',
        caption='Average power across all subjects and harmonics',
        image_format='PNG'
    )
    
    report_file = os.path.join(BASE_DIR, GROUP, f'Report_{GROUP}.html')
    report.save(report_file, overwrite=True)
    plt.close('all')

# ======================================================================
# RUN PROCESSING
# ======================================================================

if __name__ == "__main__":
    # Initialize containers for group results
    group_avg_powers = []
    appelbaum_results = []
    
    # Process each subject
    for subject in SUBJECTS:
        result = process_subject(subject)
        if result:
            appelbaum_results.append(result)
            
            # Load epochs to get info for last subject (used for group plot)
            epochs = load_epochs(subject)
    
    # Calculate group average if we have multiple subjects
    if len(group_avg_powers) > 0:
        group_avg_power = np.array(group_avg_powers).mean(axis=0)
        create_group_report(group_avg_power, epochs.info)
    
    # Save Appelbaum results to CSV
    if appelbaum_results:
        results_df = pd.DataFrame(
            appelbaum_results,
            columns=['Base', 'C5%', 'C10%', 'C20%', 'C40%', 'C80%']
        )
        results_df.insert(0, 'subj', SUBJECTS[:len(appelbaum_results)])
        
        output_file = os.path.join(
            BASE_DIR,
            f'Appelbaum_Nmax_{N_MAX_SENSORS}_{GROUP}.csv'
        )
        results_df.to_csv(output_file, index=False)
        print(f"\nSaved Appelbaum results to: {output_file}")