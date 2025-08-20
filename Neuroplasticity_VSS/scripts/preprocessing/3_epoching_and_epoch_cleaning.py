#!/usr/bin/env python
"""
MEG Epoch Processing and Cleaning Pipeline

1. Creates epochs from ICA-cleaned data
2. Performs manual epoch cleaning via visual inspection
"""

import os
import numpy as np
import mne
from mne import io
import matplotlib
matplotlib.use('TkAgg')  # Set proper matplotlib backend

# ======================
# CONFIGURATION
# ======================
BASE_PATH = '{path_to_data}'
SUBJECT = 'Subject_1'
EXPERIMENT = 'gratings'

# Epoch parameters
EVENT_IDS = {'V0':1, 'V1':2, 'V2':3, 'V3':4, 'V4':5}
TRIGGER_DELAY = 50  # ms delay compensation
EPOCH_WINDOW = (-1.0, 1.2)  # seconds (pre, post)
BASELINE = (None, 0)  # baseline correction
REJECT = dict(grad=4000e-13)  # amplitude rejection threshold

# ======================
# MAIN PROCESSING
# ======================
def main():
    # Setup paths
    ica_dir = os.path.join(BASE_PATH, SUBJECT, 'ICA_notch')
    save_dir = os.path.join(ica_dir, f'{EXPERIMENT}_epochs')
    os.makedirs(save_dir, exist_ok=True)

    # 1. Load ICA-cleaned data
    raw = io.read_raw_fif(
        os.path.join(ica_dir, f'{SUBJECT}_{EXPERIMENT}_ica-raw.fif'),
        preload=True
    )

    # 2. Find and adjust events
    events = mne.find_events(raw, stim_channel='STI101')
    events[:, 0] += int(TRIGGER_DELAY/1000 * raw.info['sfreq'])
    
    # Filter to only include our conditions (1-5)
    events = np.array([e for e in events if e[2] in EVENT_IDS.values()])

    # 3. Create epochs
    epochs = mne.Epochs(
        raw, events, EVENT_IDS,
        tmin=EPOCH_WINDOW[0],
        tmax=EPOCH_WINDOW[1],
        baseline=BASELINE,
        preload=True,
        reject=REJECT
    )

    # Save initial epochs
    epochs.save(os.path.join(save_dir, f'{SUBJECT}_all-epo.fif'), overwrite=True)

    # 4. Manual cleaning
    print("\nStarting manual epoch inspection...")
    print("Close the window when done to continue processing.")
    fig = mne.viz.plot_epochs(
        epochs,
        n_epochs=7,
        n_channels=60,
        block=True
    )

    # Save cleaned epochs
    epochs.save(os.path.join(save_dir, f'{SUBJECT}_clean-epo.fif'), overwrite=True)

    # 5. Save rejection stats
    save_rejection_stats(epochs, save_dir)

def save_rejection_stats(epochs, save_dir):
    """Save epoch counts before/after rejection"""
    counts = {}
    for cond, code in EVENT_IDS.items():
        counts[f'{cond}_pre'] = len(np.where(epochs.events[:, 2] == code)[0])
    
    with open(os.path.join(save_dir, f'{SUBJECT}_reject_stats.txt'), 'w') as f:
        f.write("Condition\tCount\n")
        for cond, count in counts.items():
            f.write(f"{cond}\t{count}\n")

if __name__ == '__main__':
    main()