"""
This script adds additional experimental variables to the reaction time data,
including block information, stimulus repetition counts, and timing between stimuli.
"""

import pandas as pd
import numpy as np
import mne
import os
from datetime import timedelta
from scipy.stats import zscore

# Configuration
DATA_PATH = '{path_to_data}'
BREAK_INFO_FILE = f'{DATA_PATH}break_info.csv'
RT_DATA_FILE = f'{DATA_PATH}response_time.csv'
OUTPUT_FILE = f'{DATA_PATH}additional_variables.csv'

# Experiment parameters
EPOCH_TYPE = '_gratings-lagcorrected-epo.fif'
ALL_EPOCH_TYPE = '_gratings_all-lagcorrected-epo.fif'
STIM_CHANNEL = "STI101"
DELAY_MS = 50  # Hardware delay compensation

def calculate_timing_variables(epochs, raw_files):
    """
    Calculate timing between consecutive stimuli and same-type stimuli.
    Returns arrays of time_to_previous and time_to_same_stimulus.
    """
    time_to_previous = [np.nan]  # First stimulus has no previous
    time_to_same = [np.nan]      # First stimulus has no same-type predecessor
    
    events = epochs.events
    
    for i in range(1, len(events)):
        # Time to previous stimulus (any type)
        time_diff = events[i][0] - events[i-1][0]
        
        # Handle negative times (across runs)
        if time_diff < 0:
            time_diff = correct_cross_run_timing(i, events, raw_files)
            
        time_to_previous.append(time_diff)
        
        # Time to previous same-type stimulus
        same_type_time = find_previous_same_type(i, events, raw_files)
        time_to_same.append(same_type_time)
    
    return time_to_previous, time_to_same

def correct_cross_run_timing(index, events, raw_files):
    """Correct timing for stimuli that span across different recording runs."""
    # Implementation depends on your specific timing correction needs
    # Placeholder for actual implementation
    return np.nan

def find_previous_same_type(index, events, raw_files):
    """Find time to previous stimulus of the same type."""
    # Implementation depends on your specific needs
    # Placeholder for actual implementation
    return np.nan

def add_block_information(df, break_info):
    """
    Add block information based on break points from break_info file.
    """
    df['block_num'] = 0  # Initialize
    
    for subject in df['subject'].unique():
        subject_info = break_info[break_info['subj'] == subject].iloc[0]
        break1 = subject_info['epoch_before_break1']
        break2 = subject_info['epoch_before_break2']
        total = subject_info['epoch_after']
        
        # Categorize epochs into blocks
        subject_mask = df['subject'] == subject
        df.loc[subject_mask & (df['orderN'] < break1), 'block_num'] = 1
        df.loc[subject_mask & (df['orderN'] >= break1) & 
                         (df['orderN'] < break1 + break2), 'block_num'] = 2
        df.loc[subject_mask & (df['orderN'] >= break1 + break2) & 
                         (df['orderN'] < break1 + break2 + total), 'block_num'] = 3
    
    return df

def main():
    # Load data
    break_info = pd.read_csv(BREAK_INFO_FILE)
    rt_data = pd.read_csv(RT_DATA_FILE)
    
    # Add block information
    rt_data = add_block_information(rt_data, break_info)
    
    # Process each subject to add timing variables
    all_time_previous = []
    all_time_same = []
    
    for subject in rt_data['subject'].unique():
        # Load MEG data
        epoch_path = f"/path/to/epochs/{subject}{ALL_EPOCH_TYPE}"
        epochs = mne.read_epochs(epoch_path, proj=False, verbose=None)
        
        # Load raw files for timing correction
        raw_files = []  # Should be populated with actual raw file paths
        
        # Calculate timing variables
        time_prev, time_same = calculate_timing_variables(epochs, raw_files)
        all_time_previous.extend(time_prev)
        all_time_same.extend(time_same)
    
    # Add timing variables to dataframe
    rt_data['time_previous'] = all_time_previous
    rt_data['time_same_stim'] = all_time_same
    
    # Save results
    rt_data.to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    main()