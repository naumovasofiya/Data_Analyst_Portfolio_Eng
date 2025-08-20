"""
MEG Data Epoch Processing Pipeline

This script performs two main operations:
1. Epochs segmentation - Creates 2-second epochs from continuous MEG data
2. Epochs cleaning - Allows visual inspection and manual rejection of bad epochs

"""

import os
import numpy as np
import mne
from mne import io
import matplotlib
matplotlib.use('TkAgg')  # Set matplotlib backend

# ======================================================================
# CONFIGURATION PARAMETERS
# ======================================================================

# Subject and experiment info
SUBJECTS = ['Subject_1']
EXPERIMENT = 'palinopsia'

# File paths
BASE_DIR = '{path_to_subjects_folders}/{subjects_folder}/'
ICA_FOLDER = 'ICA'

# Epoch segmentation parameters
EVENT_IDS = dict(C1=1, C2=2, C3=3, C4=4, C5=5)  # Event codes
TRIGGER_DELAY = 50  # ms delay to account for system latency
SKIP_INITIAL = 5    # Number of triggers to skip at start of each trial
EPOCH_LENGTH = 2000  # ms
EPOCH_STEP = 7       # Step size between epochs (controls overlap)

# ======================================================================
# PROCESSING FUNCTIONS
# ======================================================================

def create_epochs(subject):
    """Segment continuous data into 2-second epochs with optional overlap."""
    print(f"\nProcessing subject: {subject}")
    
    # Set up file paths
    subj_dir = os.path.join(BASE_DIR, subject, ICA_FOLDER)
    os.makedirs(subj_dir, exist_ok=True)
    
    # Load ICA-cleaned raw data
    raw_file = os.path.join(subj_dir, f"{subject}_{EXPERIMENT}_icapy3-raw.fif")
    raw = io.Raw(raw_file, preload=True)
    
    # Find events with adjusted timing for system delay
    events = mne.find_events(raw, stim_channel='STI101', verbose=True, 
                            shortest_event=1)
    events[:, 0] += int(TRIGGER_DELAY / 1000 * raw.info['sfreq'])
    
    # Filter events to only include our conditions
    valid_events = [e for e in events if e[2] in EVENT_IDS.values()]
    valid_events = np.array(valid_events)
    
    # Calculate inter-trial intervals
    intervals = np.diff(valid_events[:, 0], prepend=0)
    events_with_intervals = np.column_stack((valid_events, intervals))
    
    # Find trial starts (separated by >1000ms)
    trial_starts = np.where(events_with_intervals[:, 3] > 1000)[0]
    if trial_starts[0] != 0:
        trial_starts = np.insert(trial_starts, 0, 0)
    
    # Create epochs within each trial
    epoch_events = []
    for start_idx in trial_starts:
        current_pos = start_idx + 1 + SKIP_INITIAL
        start_sample = valid_events[start_idx, 0]
        
        # Create epochs until we reach the end of the 10-second trial
        while (valid_events[current_pos, 0] - start_sample) < (10000 - EPOCH_LENGTH):
            epoch_events.append(valid_events[current_pos])
            current_pos += EPOCH_STEP
    
    # Create Epochs object
    epochs = mne.Epochs(
        raw, epoch_events, EVENT_IDS,
        tmin=0, 
        tmax=EPOCH_LENGTH/1000,  # Convert ms to seconds
        baseline=None,
        proj=False,
        preload=True
    )
    
    # Save all epochs
    epochs_file = os.path.join(subj_dir, f"{subject}-all-2s-epo.fif")
    epochs.save(epochs_file, overwrite=True)
    print(f"Saved epochs to: {epochs_file}")
    
    return epochs_file

def clean_epochs(subject, epochs_file):
    """Perform visual inspection and manual rejection of bad epochs."""
    print(f"\nCleaning epochs for subject: {subject}")
    
    # Set up paths
    subj_dir = os.path.join(BASE_DIR, subject, ICA_FOLDER)
    save_path = subj_dir
    
    # Load epochs
    epochs = mne.read_epochs(epochs_file)
    
    # Count epochs per condition before rejection
    pre_rej_counts = {
        cond: len(np.where(epochs.events[:, 2] == code)[0])
        for cond, code in EVENT_IDS.items()
    }
    
    # Interactive epoch browsing for manual rejection
    print("\nStarting visual inspection...")
    print("Close the plot window when done to continue processing.")
    fig = mne.viz.plot_epochs(
        epochs,
        n_epochs=10,
        decim='auto',
        n_channels=102,
        block=True
    )
    
    # Count epochs after rejection
    post_rej_counts = {
        cond: len(np.where(epochs.events[:, 2] == code)[0])
        for cond, code in EVENT_IDS.items()
    }
    
    # Save cleaned epochs
    clean_file = os.path.join(save_path, f"{subject}-clean-epo.fif")
    epochs.save(clean_file, overwrite=True)
    print(f"Saved cleaned epochs to: {clean_file}")
    
    # Save rejection statistics
    save_rejection_stats(subject, save_path, pre_rej_counts, post_rej_counts)
    
    return clean_file

def save_rejection_stats(subject, save_path, pre_counts, post_counts):
    """Save epoch rejection statistics to a text file."""
    stats_file = os.path.join(save_path, f"{subject}_rejectstat.txt")
    
    with open(stats_file, 'w') as f:
        # Write header
        f.write("Subject  ")
        f.write("  ".join([f"{cond}_pre" for cond in EVENT_IDS]) + "  ")
        f.write("  ".join([f"{cond}_post" for cond in EVENT_IDS]) + "\n")
        
        # Write subject ID
        f.write(f"{subject}  ")
        
        # Write pre-rejection counts
        f.write("  ".join([f"{pre_counts[cond]:4d}" for cond in EVENT_IDS]) + "  ")
        
        # Write post-rejection counts
        f.write("  ".join([f"{post_counts[cond]:4d}" for cond in EVENT_IDS]))
    
    print(f"Saved rejection statistics to: {stats_file}")

# ======================================================================
# MAIN PROCESSING PIPELINE
# ======================================================================

def process_subject(subject):
    """Run complete epoch processing pipeline for one subject."""
    try:
        # Step 1: Create epochs
        epochs_file = create_epochs(subject)
        
        # Step 2: Clean epochs
        clean_epochs(subject, epochs_file)
        
        print(f"\nCompleted processing for {subject}")
    except Exception as e:
        print(f"\nError processing {subject}: {str(e)}")

# ======================================================================
# RUN PROCESSING
# ======================================================================

if __name__ == "__main__":
    for subject in SUBJECTS:
        process_subject(subject)