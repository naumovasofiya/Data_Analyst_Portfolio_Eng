# -*- coding: utf-8 -*-


"""
Gamma Power Analysis in Visual Snow Syndrome (VSS)

This script analyzes gamma-band power responses to visual grating stimuli in:
1. Healthy controls (group 1)
2. Visual Snow Syndrome patients (group 2)

Key analyses include:
- Time-frequency decomposition of MEG data
- Gamma power extraction and normalization
- Single-trial gamma peak detection
- Group-level statistical comparisons
- Visualization of results
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne
from mne.report import Report
from scipy.stats import zscore
from scipy.optimize import curve_fit
from scipy import stats

# ==============================================
# Configuration and Constants
# ==============================================

# File paths
DATA_PATH = '{path_to_original_data}'
OUTPUT_PATH = '{path_to_data}'
BREAK_INFO_FILE = f'{OUTPUT_PATH}break_info.csv'

# File naming conventions
EPOCH_TYPE = '_gratings-lagcorrected-epo.fif'
ALL_EPOCH_TYPE = '_gratings_all-lagcorrected-epo.fif'

# Subject groups
HEALTHY_SUBJECTS = ['Subject_1']
PATIENT_SUBJECTS = ['Subject_2']
ALL_SUBJECTS = HEALTHY_SUBJECTS + PATIENT_SUBJECTS

# MEG channel selection
SELECTED_CHANNELS = ['MEG1932','MEG2122','MEG2332','MEG1942','MEG1922','MEG2112','MEG2342',
                    'MEG2322','MEG1912','MEG2042','MEG2032','MEG2312','MEG2012','MEG2022',
                    'MEG1933','MEG2123','MEG2333','MEG1943','MEG1923','MEG2113','MEG2343',
                    'MEG2323','MEG1913','MEG2043','MEG2033','MEG2313','MEG2013','MEG2023']

# Experiment parameters
EVENT_IDS = dict(V0=1, V1=2, V2=3, V3=4, V4=5)  # Stimulus conditions
STIMULUS_NAMES = ['0', '0.6', '1.2', '3.6', '6.0']  # Degrees/second
FREQUENCIES = np.arange(5.0, 120, 2.5)  # Frequency range for analysis
GAMMA_RANGE = [12, 39]  # Gamma frequency range (Hz)
BASELINE = [-0.90, 0]  # Baseline period (seconds)
POST_STIM = [0.3, 1.2]  # Post-stimulus period (seconds)

# Time-frequency analysis parameters
DECIM = 50  # Downsampling factor
N_CYCLES = FREQUENCIES / 2.5  # Wavelet cycles
TIME_BANDWIDTH = 10.0  # Multitaper parameter
DELAY_MS = 50  # Hardware delay compensation

# ==============================================
# Core Analysis Functions
# ==============================================

def load_subject_data(subject):
    """Load MEG data for a single subject."""
    subj_path = f"{DATA_PATH}{subject}/ICA/gratings_epochs/"
    save_path = f"{OUTPUT_PATH}{subject}/ICA/gratings_epochs/"
    
    # Create output directory if needed
    os.makedirs(save_path, exist_ok=True)
    
    # Load epoch data
    epochs = mne.read_epochs(f"{subj_path}{subject}{EPOCH_TYPE}", 
                            proj=False, verbose=None).pick_types(meg='grad')
    all_epochs = mne.read_epochs(f"{subj_path}{subject}{ALL_EPOCH_TYPE}", 
                                proj=False, verbose=None, preload=False)
    
    return epochs, all_epochs, save_path

def process_subject_epochs(epochs, all_epochs, subject):
    """Process epoch data for a single subject."""
    # Get indices of clean epochs
    clean_indices = [i for i, element in enumerate(epochs.drop_log) if not element]
    
    # Handle special cases for certain subjects
    if subject in ['S036', 'S205', 'S211', 'S216', 'S224']:
        cutoff_values = {'S036': 109, 'S205': 0, 'S211': 260, 
                        'S216': 361, 'S224': 326}
        cutoff = cutoff_values[subject]
        clean_indices = [i-1 if i > cutoff else i for i in clean_indices]
    
    return clean_indices

def compute_time_frequency(epochs, method='multitaper'):
    """Compute time-frequency representation of epoch data."""
    method_params = {
        'n_cycles': N_CYCLES,
        'freqs': FREQUENCIES,
        'use_fft': True,
        'zero_mean': False,
        'time_bandwidth': TIME_BANDWIDTH
    }
    
    return epochs.compute_tfr(
        method, picks=SELECTED_CHANNELS, proj=False, output='power',
        average=True, return_itc=False, decim=DECIM, n_jobs=-1,
        verbose=None, **method_params
    )

def normalize_power(power, baseline_window=BASELINE):
    """Normalize power using baseline period."""
    time_points = np.arange(power.tmin, power.tmax, 1./(power.info['sfreq']/DECIM))
    baseline_points = np.intersect1d(
        np.where(baseline_window[0] <= time_points),
        np.where(time_points <= (baseline_window[1]+1e-10))
    )
    
    baseline = np.mean(power.data[:, :, baseline_points], axis=2)
    baseline_expanded = np.stack([baseline]*power.data.shape[2], axis=2)
    
    return (power.data - baseline_expanded) / baseline_expanded

def fit_gaussian_peak(frequencies, power_values):
    """Fit Gaussian curve to power spectrum to identify gamma peak."""
    def gaussian(x, a, x0, sigma):
        return a * np.exp(-(x - x0)**2 / (2 * sigma**2))
    
    # Initial parameter estimates
    max_power = np.max(power_values)
    mean_freq = np.sum(frequencies * power_values) / np.sum(power_values)
    std_freq = np.sqrt(np.sum(power_values * (frequencies - mean_freq)**2) / np.sum(power_values))
    
    try:
        popt, _ = curve_fit(
            gaussian, frequencies, power_values,
            p0=[max_power, mean_freq, std_freq],
            bounds=([0, min(frequencies), 0], [np.inf, max(frequencies), np.inf]),
            maxfev=2000
        )
        return popt
    except RuntimeError:
        return None

# ==============================================
# Main Analysis Pipeline
# ==============================================

def analyze_subject(subject, report):
    """Run full analysis pipeline for a single subject."""
    # Load data
    epochs, all_epochs, save_path = load_subject_data(subject)
    clean_indices = process_subject_epochs(epochs, all_epochs, subject)
    
    # Get event information
    events = epochs.events[:, 2]
    previous_events = [np.nan] + [events[i] for i in range(len(events)-1)]
    
    # Compute evoked responses and subtract from epochs
    evoked_responses = [epochs[cond].average(picks='grad') for cond in EVENT_IDS.values()]
    corrected_data = epochs.get_data().copy()
    
    for i, epoch in enumerate(epochs):
        stim_type = events[i] - 1  # Convert to 0-based index
        corrected_data[i] = epoch - evoked_responses[stim_type].data
    
    # Create corrected epochs object
    corrected_epochs = mne.EpochsArray(
        corrected_data, epochs.info, events=epochs.events,
        event_id=epochs.event_id, tmin=epochs.tmin, baseline=epochs.baseline
    )
    
    # Time-frequency analysis
    power = compute_time_frequency(corrected_epochs)
    norm_power = normalize_power(power)
    
    # Channel selection based on gamma power
    gamma_power = np.mean(
        norm_power[:, GAMMA_RANGE[0]:GAMMA_RANGE[1], 
        np.where((power.times >= POST_STIM[0]) & (power.times <= POST_STIM[1]))[0]],
        axis=(1,2)
    )
    
    top_channels = [
        power.info['ch_names'][i] 
        for i in np.argsort(gamma_power)[-5:]  # Select top 5 channels
    ]
    
    # Analyze single trials
    single_trial_results = analyze_single_trials(
        corrected_epochs, events, clean_indices, top_channels, subject
    )
    
    return single_trial_results

def analyze_single_trials(epochs, events, clean_indices, top_channels, subject):
    """Analyze gamma responses in single trials."""
    results = {
        'subject': [], 'group': [], 'trial_num': [],
        'stim_type': [], 'prev_stim': [], 'gamma_power': [],
        'gamma_freq': [], 'baseline_power': []
    }
    
    # Determine subject group (1=healthy, 2=VSS)
    group = 1 if subject[1] == '0' else 2
    
    # Time-frequency analysis for single trials
    tfr = epochs.compute_tfr(
        'multitaper', picks=top_channels, proj=False, output='power',
        average=False, return_itc=False, decim=DECIM, n_jobs=-1,
        verbose=None, n_cycles=N_CYCLES, freqs=FREQUENCIES,
        use_fft=True, zero_mean=False, time_bandwidth=TIME_BANDWIDTH
    )
    
    # Normalize power
    baseline_power = np.mean(
        tfr.data[:, :, np.where(
            (tfr.times >= BASELINE[0]) & (tfr.times <= BASELINE[1])
        )[0]],
        axis=2
    )
    norm_power = (tfr.data - np.stack([baseline_power]*tfr.data.shape[2], axis=2)) / np.stack([baseline_power]*tfr.data.shape[2], axis=2)
    
    # Analyze each trial
    for trial_idx in clean_indices:
        # Get trial data
        trial_power = np.mean(
            norm_power[trial_idx, :, 
            np.where((tfr.times >= POST_STIM[0]) & (tfr.times <= POST_STIM[1]))[0]],
            axis=1
        )
        trial_freqs = FREQUENCIES[GAMMA_RANGE[0]:GAMMA_RANGE[1]]
        trial_power_vals = np.mean(
            norm_power[trial_idx, GAMMA_RANGE[0]:GAMMA_RANGE[1], 
            np.where((tfr.times >= POST_STIM[0]) & (tfr.times <= POST_STIM[1]))[0]],
            axis=1
        )
        
        # Fit Gaussian to identify gamma peak
        fit_result = fit_gaussian_peak(trial_freqs, trial_power_vals)
        
        # Store results
        results['subject'].append(subject)
        results['group'].append(group)
        results['trial_num'].append(trial_idx)
        results['stim_type'].append(events[trial_idx])
        results['prev_stim'].append(events[trial_idx-1] if trial_idx > 0 else np.nan)
        results['gamma_power'].append(np.mean(trial_power))
        results['baseline_power'].append(np.mean(baseline_power[trial_idx]))
        
        if fit_result is not None:
            results['gamma_freq'].append(fit_result[1])  # Peak frequency
        else:
            results['gamma_freq'].append(np.nan)
    
    return results

# ==============================================
# Visualization Functions
# ==============================================

def plot_group_results(healthy_data, patient_data):
    """Create summary plots comparing healthy and VSS groups."""
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ['black', '#6F4E37', 'blue', 'green', 'red']
    degree_sign = u'\N{DEGREE SIGN}'
    
    # Calculate confidence intervals
    healthy_ci = []
    patient_ci = []
    
    for i in range(5):  # For each stimulus condition
        # Healthy group
        healthy_mean = np.mean(healthy_data[i], axis=0)
        healthy_sem = stats.sem(healthy_data[i], axis=0)
        healthy_ci.append((healthy_mean - 1.96*healthy_sem, healthy_mean + 1.96*healthy_sem))
        
        # Patient group
        patient_mean = np.mean(patient_data[i], axis=0)
        patient_sem = stats.sem(patient_data[i], axis=0)
        patient_ci.append((patient_mean - 1.96*patient_sem, patient_mean + 1.96*patient_sem))
    
    # Plot results
    for i in range(5):
        # Healthy controls (dashed lines)
        ax.plot(
            FREQUENCIES[GAMMA_RANGE[0]:GAMMA_RANGE[1]], 
            healthy_mean, 
            linestyle='--', color=colors[i], 
            label=f'{STIMULUS_NAMES[i]}{degree_sign}/s', 
            linewidth=4, alpha=0.9
        )
        ax.fill_between(
            FREQUENCIES[GAMMA_RANGE[0]:GAMMA_RANGE[1]],
            healthy_ci[i][0], healthy_ci[i][1],
            color=colors[i], alpha=0.1
        )
        
        # VSS patients (solid lines)
        ax.plot(
            FREQUENCIES[GAMMA_RANGE[0]:GAMMA_RANGE[1]], 
            patient_mean, 
            linestyle='-', color=colors[i], 
            linewidth=4, alpha=0.9
        )
        ax.fill_between(
            FREQUENCIES[GAMMA_RANGE[0]:GAMMA_RANGE[1]],
            patient_ci[i][0], patient_ci[i][1],
            color=colors[i], alpha=0.1
        )
    
    # Format plot
    ax.set_xlabel('Frequency [Hz]', fontsize=40)
    ax.set_ylabel('Gamma response power [a.u.]', fontsize=40)
    ax.tick_params(axis='both', which='major', labelsize=30)
    
    # Create custom legend
    handles, labels = ax.get_legend_handles_labels()
    handles = [plt.Line2D([0], [0], color='none')] + handles[:5] + [plt.Line2D([0], [0], color='none')] + handles[5:]
    labels = ['Control'] + labels[:5] + ['VSS'] + labels[5:]
    
    ax.legend(
        handles, labels, loc='upper right', fontsize=28,
        bbox_to_anchor=(1.2, 1), borderaxespad=0, ncols=1,
        title='Drift rate', title_fontsize=33, edgecolor='black'
    )
    
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_PATH}group_comparison.pdf",
        format="pdf", bbox_inches="tight"
    )
    plt.close()

# ==============================================
# Main Execution
# ==============================================

def main():
    # Initialize data storage
    all_results = []
    healthy_group_data = [[] for _ in range(5)]  # 5 stimulus conditions
    patient_group_data = [[] for _ in range(5)]
    
    # Create report
    report = Report()
    
    # Process each subject
    for subject in ALL_SUBJECTS:
        print(f"Processing subject {subject}...")
        
        try:
            # Run analysis
            subject_results = analyze_subject(subject, report)
            all_results.append(subject_results)
            
            # Organize data by group and condition
            group_idx = 0 if subject[1] == '0' else 1  # 0=healthy, 1=VSS
            
            for cond in range(5):
                cond_data = [
                    res['gamma_power'] for res in subject_results 
                    if res['stim_type'] == cond+1
                ]
                
                if group_idx == 0:
                    healthy_group_data[cond].extend(cond_data)
                else:
                    patient_group_data[cond].extend(cond_data)
                    
        except Exception as e:
            print(f"Error processing subject {subject}: {str(e)}")
            continue
    
    # Save all results to CSV
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(f"{OUTPUT_PATH}gamma_analysis_results.csv", index=False)
    
    # Create group comparison plot
    plot_group_results(healthy_group_data, patient_group_data)
    
    # Save report
    report.save(f"{OUTPUT_PATH}analysis_report.html", overwrite=True)

if __name__ == "__main__":
    main()