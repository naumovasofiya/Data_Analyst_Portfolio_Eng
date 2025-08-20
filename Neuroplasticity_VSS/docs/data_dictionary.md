Data Dictionary

gamma_stim.csv - Stimulus-Condition Level Data
| Variable       | Description                                  | Units/Values               |
|----------------|----------------------------------------------|----------------------------|
| code           | Subject identifier                           |                            |
| group          | Participant group                            | 1=Control, 2=VSS           |
| V0_ampl        | Gamma power for static grating (0°/s)        | Normalized power (dB)      |
| V0_freq        | Peak gamma frequency for 0°/s                | Hz                         |
| V1_ampl        | Gamma power for 0.6°/s drift                 | Normalized power (dB)      |
| V1_freq        | Peak gamma frequency for 0.6°/s              | Hz                         |
| V2_ampl        | Gamma power for 1.2°/s drift                 | Normalized power (dB)      |
| V2_freq        | Peak gamma frequency for 1.2°/s              | Hz                         |
| V3_ampl        | Gamma power for 3.6°/s drift                 | Normalized power (dB)      |
| V3_freq        | Peak gamma frequency for 3.6°/s              | Hz                         |
| V4_ampl        | Gamma power for 6.0°/s drift                 | Normalized power (dB)      |
| V4_freq        | Peak gamma frequency for 6.0°/s              | Hz                         |

gamma_all.csv - Trial-Level Data
| Variable          | Description                                  | Units/Values               |
|-------------------|----------------------------------------------|----------------------------|
| code              | Subject identifier                           | S001-S228                  |
| group             | Participant group                            | 1=Control, 2=VSS           |
| orderN            | Trial sequence number                        | 0-136 (total trials)       |
| stim_type         | Stimulus condition                           | 1=0°/s, 2=0.6°/s, 3=1.2°/s, 4=3.6°/s, 5=6.0°/s |
| previous_stim     | Previous trial's stimulus type               | Same as stim_type          |
| baseline_power    | Pre-stimulus baseline power                  | dB                         |
| gamma_power       | Normalized gamma-band power response         | dB                         |
| gamma_freq        | Peak frequency in gamma band                 | Hz                         |
| gamma_freq_old    | Alternative frequency measure (legacy)       | Hz                         |
| block_num         | Experimental block number                    | 1-3                        |
| repetitionN       | Stimulus repetition count                    | 0+ (within block)          |
| time_previous     | Time since previous stimulus                 | ms                         |
| time_same_stim    | Time since same stimulus type                | ms                         |
| reaction_time     | Response latency                             | ms                         |
| reaction_type     | Response accuracy classification             | 0=correct, 1=late, 2=miss  |

Experimental Conditions Reference
1 = Static (0°/s)  
2 = Slow drift (0.6°/s)  
3 = Medium drift (1.2°/s)  
4 = Fast drift (3.6°/s)  
5 = Very fast drift (6.0°/s)

Response Type Classification
0 = Correct response (150-1000ms post-offset)  
1 = Late response (>1000ms)  
2 = Missed response (no button press)

Notes
- Power values normalized to pre-stimulus baseline (-0.9 to 0s)
- Gamma frequency range: 30-100Hz
- Negative reaction_time indicates anticipatory response
- Missing frequency values indicate failed Gaussian fitting