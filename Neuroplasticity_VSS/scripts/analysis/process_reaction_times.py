"""
This script processes reaction time data from visual grating experiments.
It extracts response types and reaction times from log files and matches them with MEG epochs.
The results are saved to CSV files for further analysis.
"""

import numpy as np
import pandas as pd
import os
import mne

# Subject lists
HEALTHY_SUBJECTS = ['Subject_1']
PATIENT_SUBJECTS = ['Subject_2']
ALL_SUBJECTS = HEALTHY_SUBJECTS + PATIENT_SUBJECTS

# File paths
DATA_PATH = '{path_to_original_data}'
RESULTS_PATH = "{path_to_original_data}/Results/"
OUTPUT_PATH = '{path_to_data}'

# Experiment parameters
RESPONSE_WINDOW = 1700  # Time window for valid responses in ms (1.7 seconds)
STIM_CHANNEL = 'STI101'
EPOCH_TYPE = '_gratings-lagcorrected-epo.fif'
ALL_EPOCH_TYPE = '_gratings_all-lagcorrected-epo.fif'

def process_subject_log(subject):
    """
    Process log file for a single subject and extract response data.
    Returns response types and time differences for valid trials.
    """
    # Determine log file path based on subject group
    if subject in ['']:
        log_path = f'{OUTPUT_PATH}{subject}-Gratings_visual_snow.log'
    else:
        log_path = f'/{path_to_original_data}/Logfiles/{subject}-Gratings_visual_snow.log'
    
    if not os.path.exists(log_path) or subject in ['S016','S222']:
        return None, None, None, None

    # Load and preprocess log file
    log_data = pd.read_csv(log_path)
    log_data = log_data[["Code", "Time"]].transpose().values.tolist()
    
    # Extract relevant events and times
    grating_events = [e for e in log_data[0] if e in ['gr_0', 'gr_1', 'gr_2', 'gr_3', 'gr_4']]
    event_times = [log_data[1][i] for i in range(len(log_data[0])) if log_data[0][i] in grating_events]
    
    # Special handling for specific subjects
    if subject == '':
        grating_events = grating_events[5:]
        event_times = event_times[5:]
    
    return grating_events, event_times, log_data

def classify_responses(log_data):
    """
    Classify responses from log data into correct/error/late categories.
    """
    response_types = []
    time_differences = []
    
    i = 0
    while i < len(log_data[0]):
        label = str(log_data[0][i])
        
        if label.startswith('gr_'):  
            disappear_time = None
            response_time = None
            late_time = None
            
            # Parse stimulus block
            while i < len(log_data[0]) and log_data[0][i] not in ['fix', 'anim']:
                current_label = str(log_data[0][i])
                if current_label == 'disappear':
                    disappear_time = log_data[1][i]
                elif current_label == '16':
                    response_time = log_data[1][i]
                elif current_label == 'late':
                    late_time = log_data[1][i]
                i += 1
            
            # Classify response
            if disappear_time is not None:
                if response_time is not None:
                    time_diff = response_time - disappear_time
                    if response_time < disappear_time:
                        response_class = 0  # Error (early response)
                    elif disappear_time <= response_time <= disappear_time + RESPONSE_WINDOW:
                        response_class = 0  # Correct response
                    elif late_time is not None and response_time > late_time:
                        response_class = 2  # Late response
                    elif disappear_time + RESPONSE_WINDOW < response_time and late_time is None and time_diff < 10000:
                        response_class = 1  # Late but within extended window
                    else:
                        response_class = 2  # Very late
                elif late_time is not None:
                    response_class = 2  # No response, marked late
                    time_diff = np.nan
                else:
                    response_class = 2  # No response at all
                    time_diff = np.nan
            else:
                response_class = 3  # Invalid trial
                time_diff = np.nan
            
            response_types.append(response_class)
            time_differences.append(time_diff)
        else:
            i += 1
    
    return response_types, time_differences

def main():
    all_response_data = []
    
    for subject in ALL_SUBJECTS:
        # Process log file
        grating_events, event_times, log_data = process_subject_log(subject)
        if grating_events is None:
            continue
            
        # Load MEG epochs
        epoch_path = f'{DATA_PATH}{subject}/ICA_notch/gratings_epochs/{subject}{EPOCH_TYPE}'
        epochs = mne.read_epochs(epoch_path, proj=False, verbose=None).pick_types(meg='grad')
        valid_indices = [i for i, element in enumerate(epochs.drop_log) if not element]
        
        # Classify responses
        response_types, time_differences = classify_responses(log_data)
        
        # Store results
        subject_data = {
            'subject': subject,
            'group': 0 if subject[1] == '0' else 1,  # 0=healthy, 1=patient
            'events': grating_events,
            'times': event_times,
            'response_types': response_types,
            'time_differences': time_differences,
            'valid_indices': valid_indices
        }
        all_response_data.append(subject_data)
    
    # Save results to CSV
    results_df = pd.DataFrame(all_response_data)
    results_df.to_csv(f'{OUTPUT_PATH}response_time.csv', index=False)

if __name__ == "__main__":
    main()