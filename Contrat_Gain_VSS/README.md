# Investigation of Contrast Gain Control in Visual Snow Syndrome Using Magnetoencephalography

[Presentation](https://github.com/naumovasofiya/MEG-Analysis-of-Neuroplasticity-in-VSS/blob/796c0b48c364a384ec33c5289841a1fd5b607580/Contrast_Gain_VSS/results/figures_and_presentation/conrast%20gain%20control%20in%20the%20VSS.pdf)

## Research Objective
To investigate the balance of excitation and inhibition (E/I) processes in the visual cortex of individuals with Visual Snow Syndrome (VSS) using steady-state visually evoked magnetic fields (SSVEF).

## Research Tasks
1. Investigate visual cortex excitability in participants with VSS and a control group by assessing contrast gain control
2. Examine the correlation between contrast saturation and the severity of visual discomfort

## Methods and Materials
### Participants:
- 23 individuals with VSS (14 men, 9 women, mean age 27±5.52 years)
- 28 control subjects (16 men, 12 women, mean age 27.46±4.49 years)

### Equipment:
- MEG system "Elekta Neuromag Vector View" (204 planar gradiometers)
- Magnetically shielded room "Ak3B"
- Presentation software for stimulation

### Paradigm:
- Stimuli: black-and-white horizontal sinusoidal gratings (2 cycles/degree)
- 5 contrast levels (5%, 10%, 20%, 40%, 80%)
- Reversal frequency: 6.666 Hz
- 5 blocks of 10 sec per contrast

### Data Analysis:
1. Preprocessing:
   - Artifact correction (MaxFilter, tSSS)
   - ICA for biological artifact removal
   - Segmentation into 2-second epochs

2. Spectral Analysis:
   - Welch's method (psd_welch, MNE-Python)
   - Power analysis at stimulation frequency and harmonics

3. Modeling:
   - Contrast response function (modified Naka-Rushton equation):
     ```
     R = Rmax * C^n / (C50^sn + C^sn) + b
     ```
   - Key parameter: saturation exponent "s"

4. Statistics:
   - Student's t-test / Mann-Whitney U test
   - Correlation analysis (Spearman)

## Key Results
1. **Contrast Gain**:
   - Saturation parameter "s" did not differ between control subjects and VSS patients (U = 125.0, p=0.167)
   - Control group showed saturation/oversaturation at high contrasts
   - VSS group showed a tendency toward reduced saturation across various contrast levels

2. **Visual Discomfort**:
   - Significantly higher in the VSS group (U = 330.5, p<0.001)
   - No correlation with parameter "s" was found (r=0.26, p=0.399)

3. **SSVEF Amplitude**:
   - Maximum response at the 2nd harmonic (~13.2 Hz)
   - No significant between-group differences in amplitudes at all contrast levels

## Conclusions
1. Contrast response saturation in visual cortex responses, measured using steady-state visually evoked fields, does not differ between individuals with visual snow syndrome and the control group
2. The level of visual discomfort when perceiving high-contrast visual patterns is increased in individuals with visual snow syndrome compared to the control group
3. High interindividual variability in the contrast gain saturation parameter indicates heterogeneity of VSS
4. The absence of correlation between visual discomfort level and contrast gain saturation suggests that this feature of visual cortex excitability is not the primary cause of visual discomfort in visual snow syndrome

## Future Directions
1. Source localization using individual MRI data
2. Investigation of separate contributions of parvo- and magnocellular pathways
3. Development of adapted questionnaires for symptom assessment
4. Testing of new therapeutic approaches