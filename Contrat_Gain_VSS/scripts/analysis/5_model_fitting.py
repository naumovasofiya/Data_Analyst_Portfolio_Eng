"""
MEG Contrast Response Function Fitting Pipeline

This script performs:
1. Loading of preprocessed PSD data
2. Fitting of contrast response functions using Naka-Rushton model
3. Generation of fitting reports
4. Saving of fitting parameters for statistical analysis

"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy import mean
from lmfit import minimize, Parameters
import mne
from mne.report import Report

# ======================================================================
# CONFIGURATION PARAMETERS
# ======================================================================

# Subject groups
SUBJECTS_VS = ['Subject_1']  # Visual Snow group
SUBJECTS_CONTR = []     # Control group

# File paths
BASE_DIR = '{path_to_subjects_folders}/{subjects_folder}/'
INPUT_FILES = ['Appelbaum_Nmax_1']  # Input data files

# Experiment parameters
CONTRASTS = np.array([0.05, 0.1, 0.2, 0.4, 0.8])  # Contrast levels
FINE_CONTRAST = np.linspace(0.05, 0.8, 100)       # For smooth model curve

# Model fitting parameters
INITIAL_PARAMS = {
    'semisaturation': 0.3,
    'MAXampl': None,  # Will be set to max(data)
    'Saturation': 1.0,
    'baseline': None  # Will be set from data
}

PARAM_CONSTRAINTS = {
    'semisaturation': (0.0, 50.0),
    'Saturation': (0.0, 5.0),
    'baseline': (0.0, None)
}

# Plotting parameters
PLOT_FONT = {
    'family': 'serif',
    'color': 'darkred',
    'weight': 'normal',
    'size': 14
}

# ======================================================================
# MODEL FUNCTIONS
# ======================================================================

def naka_rushton(params, contrast):
    """
    Naka-Rushton contrast response function.
    
    Parameters:
    -----------
    params : lmfit.Parameters
        Contains model parameters:
        - semisaturation: contrast at half-max response
        - MAXampl: maximum response amplitude
        - Saturation: saturation exponent
        - baseline: baseline response level
    
    contrast : array-like
        Input contrast values
        
    Returns:
    --------
    array-like: Model predictions
    """
    semisat = params['semisaturation'].value
    Rmax = params['MAXampl'].value
    s = params['Saturation'].value
    b = params['baseline'].value
    
    return Rmax * contrast**2 / (semisat**(2*s) + contrast**(2*s)) + b

def residual(params, contrast, data):
    """
    Residual function for model fitting.
    
    Parameters:
    -----------
    params : lmfit.Parameters
        Model parameters
    contrast : array-like
        Input contrast values
    data : array-like
        Observed data
        
    Returns:
    --------
    array-like: Difference between model and data
    """
    return data - naka_rushton(params, contrast)

# ======================================================================
# PROCESSING FUNCTIONS
# ======================================================================

def load_subject_data(csv_path, group, subject, data_file):
    """
    Load subject data from CSV file.
    
    Parameters:
    -----------
    csv_path : str
        Base directory path
    group : str
        Group name ('VS' or 'CONTR')
    subject : str
        Subject ID
    data_file : str
        Data file name
        
    Returns:
    --------
    tuple: (data, baseline) both scaled by 1e12
    """
    df = pd.read_csv(f"{csv_path}{data_file}_{group}.csv")
    subject_data = df[df['subj'] == subject].iloc[0]
    
    # Convert to picoTesla
    scale = 1e12
    data = np.array(subject_data[['C5%', 'C10%', 'C20%', 'C40%', 'C80%']]) * scale
    baseline = subject_data['Base'] * scale
    
    return data, baseline

def initialize_parameters(data, baseline):
    """
    Initialize model parameters with constraints.
    
    Parameters:
    -----------
    data : array-like
        Response data
    baseline : float
        Baseline response level
        
    Returns:
    --------
    lmfit.Parameters: Initialized parameters
    """
    params = Parameters()
    
    # Add parameters with initial values
    params.add('semisaturation', value=INITIAL_PARAMS['semisaturation'], 
               min=PARAM_CONSTRAINTS['semisaturation'][0],
               max=PARAM_CONSTRAINTS['semisaturation'][1])
    
    params.add('MAXampl', value=np.max(data),
               min=0)  # Response can't be negative
    
    params.add('Saturation', value=INITIAL_PARAMS['Saturation'],
               min=PARAM_CONSTRAINTS['Saturation'][0],
               max=PARAM_CONSTRAINTS['Saturation'][1])
    
    params.add('baseline', value=baseline,
               min=PARAM_CONSTRAINTS['baseline'][0],
               vary=True)
    
    return params

def create_fitting_report(subject_path, subject, data_file):
    """
    Initialize or load existing report.
    
    Parameters:
    -----------
    subject_path : str
        Path to subject directory
    subject : str
        Subject ID
    data_file : str
        Data file name
        
    Returns:
    --------
    mne.Report: Report object
    """
    report_file = f"{subject_path}Fit_{subject}.hdf5"
    
    if os.path.exists(report_file):
        return mne.open_report(report_file)
    else:
        return mne.Report(
            title=f"Fit contrast gain function for {data_file} - subj: {subject}"
        )

def plot_results(contrast, data, model, fine_model, residuals, params, rsq, subject, data_file):
    """
    Create fitting results plot.
    
    Parameters:
    -----------
    contrast : array-like
        Experimental contrast levels
    data : array-like
        Observed data
    model : array-like
        Fitted model at experimental contrasts
    fine_model : array-like
        Model at fine contrast resolution
    residuals : array-like
        Residuals from fit
    params : lmfit.Parameters
        Fitted parameters
    rsq : float
        R-squared value
    subject : str
        Subject ID
    data_file : str
        Data file name
        
    Returns:
    --------
    matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots()
    
    # Plot data and models
    ax.plot(contrast, model, label='Fit')
    ax.plot(contrast, residuals, label='Residuals')
    ax.plot(contrast, data, '+', label='Data')
    ax.plot(FINE_CONTRAST, fine_model, '--r', label='Model')
    
    # Format plot
    ax.set_xscale("log")
    ax.set_xticks(contrast)
    ax.set_xticklabels(contrast)
    ax.legend()
    
    # Add parameter text
    param_text = (
        f"semi={params['semisaturation'].value:.2f}\n"
        f"Rmax={params['MAXampl'].value:.2f}\n"
        f"s={params['Saturation'].value:.2f}\n"
        f"b={params['baseline'].value:.4f}\n"
        f"R²={rsq:.2f}"
    )
    ax.text(0.4, np.min(data), param_text, fontdict=PLOT_FONT)
    ax.set_title(f"{subject}_{data_file}")
    
    return fig

# ======================================================================
# MAIN PROCESSING PIPELINE
# ======================================================================

def process_subject(group, subject, data_file):
    """
    Process a single subject's data.
    
    Parameters:
    -----------
    group : str
        Group name ('VS' or 'CONTR')
    subject : str
        Subject ID
    data_file : str
        Data file name
        
    Returns:
    --------
    tuple: (subject_id, fitting_results)
    """
    print(f"\nProcessing {subject} from {group} group")
    
    try:
        # Set up paths
        subject_path = f"{BASE_DIR}{group}/{subject}/"
        
        # Load data
        data, baseline = load_subject_data(BASE_DIR, group, subject, data_file)
        
        # Initialize model parameters
        params = initialize_parameters(data, baseline)
        
        # Perform fitting
        result = minimize(residual, params, args=(CONTRASTS, data))
        
        # Calculate model predictions
        final_fit = data - result.residual
        fine_model = naka_rushton(result.params, FINE_CONTRAST)
        
        # Calculate goodness of fit
        rss = (result.residual**2).sum()
        tss = sum(np.power(data - mean(data), 2))
        rsq = 1 - rss/tss
        
        print(f"Fit results for {subject}:")
        print(f"  RSS = {rss:.1f}, TSS = {tss:.1f}, R² = {rsq:.3f}")
        
        # Create and save report
        report = create_fitting_report(subject_path, subject, data_file)
        fig = plot_results(
            CONTRASTS, data, final_fit, fine_model, 
            result.residual, result.params, rsq, subject, data_file
        )
        
        report.add_figure(
            fig, 
            title=data_file, 
            caption="Naka-Rushton fit results", 
            image_format='PNG'
        )
        
        report.save(f"{subject_path}Fit_smax2_Nmax1_min{subject}.hdf5", overwrite=True)
        report.save(f"{subject_path}Fit_smax2_Nmax1_min{subject}.html", overwrite=True)
        
        # Return fitting results
        fit_results = [
            result.params['semisaturation'].value,
            result.params['MAXampl'].value,
            result.params['Saturation'].value,
            result.params['baseline'].value,
            rsq
        ]
        
        return subject, fit_results
    
    except Exception as e:
        print(f"Error processing {subject}: {str(e)}")
        return None

# ======================================================================
# RUN PROCESSING
# ======================================================================

if __name__ == "__main__":
    all_results = []
    subject_ids = []
    
    # Process all subject groups
    for group, subjects in [('VS', SUBJECTS_VS), ('CONTR', SUBJECTS_CONTR)]:
        for subject in subjects:
            for data_file in INPUT_FILES:
                result = process_subject(group, subject, data_file)
                if result:
                    subject_id, fit_results = result
                    subject_ids.append(subject_id)
                    all_results.append(fit_results)
    
    # Save all results to CSV
    if all_results:
        results_df = pd.DataFrame(
            np.array(all_results).T,
            columns=subject_ids,
            index=['AbN1_semi', 'AbN1_Rmax', 'AbN1_s', 'AbN1_b', 'AbN1_R2']
        ).T.reset_index().rename(columns={'index': 'subj'})
        
        output_file = f"{BASE_DIR}fit_results_all_smax2_Nmax1.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\nSaved all results to: {output_file}")
    
    plt.close('all')