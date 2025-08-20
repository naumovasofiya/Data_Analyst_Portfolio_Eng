# Visual Snow Syndrome (VSS) Gamma Oscillations Study Protocol

## 1. Participant Information

### Groups:
- **Healthy controls**: IDs starting with 'X0'
- **VSS patients**: IDs starting with 'X1' or 'X2'

### Exclusions:
- Subjects XXX and YYY (response time analysis)
- Subject RRR (gamma analysis)

## 2. Stimulus Paradigm

### Visual Stimuli:
- High-contrast annular gratings

### Motion Conditions:
1. **V0**: Static (0°/s)
2. **V1**: Slow drift (0.6°/s)
3. **V2**: Medium drift (1.2°/s)
4. **V3**: Fast drift (3.6°/s)
5. **V4**: Very fast drift (6.0°/s)

### Trial Structure:
1. Fixation cross (1.2s)
2. Grating presentation (1.2-1.6s)
3. Response window:
   - Primary: 150ms-1.7s post-offset
   - Extended: Up to 2s for late responses

## 3. Data Acquisition

### MEG System:
- Elekta Neuromag 306-channel

### Parameters:
- Sampling rate: 1000Hz
- Filters: 0.1-330Hz
- Stimulus channel: STI101

### Auxiliary Channels:
- ECG: ECG063
- Vertical EOG: EOG061
- Horizontal EOG: EOG062

## 4. Processing Pipeline

### 4.1 MaxFilter (tSSS):
- Applied during initial data conversion
- Movement compensation

### 4.2 Preprocessing:
- Notch filtering (50Hz + harmonics)
- ICA-based artifact removal
- 50ms hardware delay compensation

### 4.3 Epoching:
- Time-locked to stimulus onset
- Baseline correction (-0.9 to 0s)
- Manual trial rejection

### 4.4 Gamma Analysis:
- Frequency range: 30-100 Hz
- Multitaper time-frequency analysis
- Single-trial peak detection
- Selected channels: 28 gradiometers showing strongest gamma response

## 5. Analysis Parameters

### Time-Frequency:
- **Frequencies**: 5-120Hz in 2.5Hz steps
- **Wavelet cycles**: FREQUENCIES/2.5
- **Time-bandwidth**: 10.0
- **Downsampling**: 50x

### Statistical Models:
- Non-linear power decay (exponential + linear)
- Linear mixed-effects models for group comparisons
- Block-wise ANOVA (3 blocks per session)
