Data Structures

"Key Name"	*Datatype*	(Explanation)

Submission	*Dictionary*	(Container for all the items computed)
|
 -> "Version"		*DataFrame*	(Austenite Calculator Version)
 -> "Phase_Info"	*DataFrame*	(number, conversions, etc)
    |
   -> "Crystal"		RENAME
   -> "Cell"		RENAME
 -> Diffractometer Info (beam Shape, detector position)
 -> MCMC parameters
 -> "File_Paths"	*Dictionary*	(File/Folder paths)
    |
   -> "Data_Directory"		*String*
   ->"Working_Directory"	*String*
   ->"Cif_Filenames"		*List*
   ->"Diffraction_Filenames" 	*List*
   ->"Instrument_Filename"	*String*
   ->"JSON_Filename"		*String*

 -> Dataset
   |
   -> "Flags" 		*DataFrame*	(Comments/Flags for the user, fit issues, offset)
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

Mutability
	dictionaries and DataFrames should be mutable, so you don't need to pass the object back from a function


Flags syntax:

        value: numeric value (float) of flagged value
        source: short string text explaining the what step in the data is flagged
        flag: longer string text describing the alert to user
        suggestion: string text with suggestions on source or mitigation methods to decrease error