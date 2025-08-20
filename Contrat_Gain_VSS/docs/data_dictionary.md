Data Dictionary

model_fitting_results.csv - Naka-Rushton Model Parameters
| Variable       | Description                                   | Units/Values               |
|----------------|-----------------------------------------------|----------------------------|
| subj           | Subject identifier                            |                            |
| AbN1_semi      | Semi-saturation contrast (c50)                | Unitless (fitted parameter)|
| AbN1_Rmax      | Maximum response amplitude (Rmax)             | Unitless (fitted parameter)|
| AbN1_s         | Slope parameter (s)                           | Unitless (fitted parameter)|
| AbN1_b         | Baseline parameter (b)                        | Unitless (fitted parameter)|
| AbN1_R2        | Goodness-of-fit (R-squared)                   | 0-1 (1 = perfect fit)      |

response_power.csv - Contrast Response Data
| Variable       | Description                                   | Units/Values                       |
|----------------|-----------------------------------------------|------------------------------------|
| subj           | Subject identifier                            |                                    |
| group          | Participant group                             | 1=Control, 2=VSS                   |
| C5%            | Gamma power at 5% contrast                    | Normalized power (arbitrary units) |
| C10%           | Gamma power at 10% contrast                   | Normalized power (arbitrary units) |
| C20%           | Gamma power at 20% contrast                   | Normalized power (arbitrary units) |
| C40%           | Gamma power at 40% contrast                   | Normalized power (arbitrary units) |
| C80%           | Gamma power at 80% contrast                   | Normalized power (arbitrary units) |

- Notes:
1. Naka-Rushton function: R(c) = Rmax * (c^n / (c^n + c50^n)) + b
2. Group codes: 1=Control, 2=VSS (Visual Snow Syndrome)
3. Power values are normalized 

4. Small parameter values (e.g., 1.85E-10) indicate failed fits
