Data Structures

"Key Name"	*Datatype*	(Explanation)

Submission
|
 -> "Version"	*DataFrame*	(Austenite Calculator Version)
 -> Phase Info (number, conversions, etc)
 -> Diffractometer Info (beam Shape, detector position)
 -> MCMC parameters
 -> Dataset
   |
   -> Comments/Flags (fit issues, offset)
   -> Histogram Data (raw data)
   -> Fit Data
   -> MCMC Uncertainty Inputs
   -> MCMC Distribution Data (8000 normalized intensities)
   -> Phase Fraction Data (8000 n_ints run through phase frac calc)
   -> Peak
    |
    -> LeBail Fit (values, uncertainties)
    -> Peak Fit (values, uncertainties)
    -> Gaussian Fit (values, uncertainties)
    -> Theoretical Intensities
    -> hkl, multiplicity
    -> Phase
    -> Crystallites Illuminated