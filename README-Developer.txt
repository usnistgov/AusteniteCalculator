Data Structures

"Key Name"	*Datatype*	(Explanation)

Submission	*Dictionary*	(Container for all the items computed)
|
 -> "Version"		*DataFrame*	(Austenite Calculator Version)
 -> "Phase_Info"	*DataFrame*	(number, conversions, etc)
 -> 
    |

   -> "Interaction_Parameters"		(currently has keys: 'austenite-SRM487.cif', 'ferrite-SRM487.cif', 'beam_shape', 'beam_size', 'raster_x', 'raster_y', 'sample_displacement', 'L', 'W_F', 'H_F', 'H_R'	.cif file rows have the powder size, number of particles, rocking angle

   -> "Unit_Cell"		*DataFrame*  (currently has columns: ['scattering_dict', 'elem_fractions_dict',
       'cell_volumes_dict', 'cell_masses_dict'] for rows of cif files
	|
	-> scattering_dict  *Series, by cif file* with list of lists with columns for elem_sym, f', f'', mu, number of atoms per cell
	-> elem_fractions_dict list with the amount of each element

	-> 'unit_cell_volume_CIF' *DataFrame* with the volumes for each unit cell from the CIF file	
	-> 'unit_cell_mass_CIF' *DataFrame* with the mass for each unit cell from the CIF file
   -> "Atomic_Masses"  		*DataFrame*  has 'atomic_masses_dict' for rows of elements listed


 -> Diffractometer Info (beam Shape, detector position)
 -> MCMC parameters
 -> "File_Paths"	*Dictionary*	(File/Folder paths)
    |
   -> "Data_Directory"		*String*
   -> "Working_Directory"	*String*
   -> "Cif_Filenames"		*List*
   -> "Diffraction_Filenames" 	*List*
   -> "Instrument_Filename"	*String*
   -> "JSON_Filename"		*String*
   -> "Dataset_name"		*List*


 -> Dataset *Dictionary*
   |
   -> "Flags" 		*DataFrame*	(Comments/Flags for the user, fit issues, offset)
   -> "X_Range"	*list* [xmin, xmax]
   -> Histogram Data (raw data)
   -> "Le_Bail_Data" *dict* Le Bail Fit Data		(phase fractions, unit cell, fit values and uncertainties)
   -> "Peak_Fit_Data" *dict* GSAS-II format
   -> "Prelim_Phase_Fraction" *DataFrame*
   -> "Prelim_Aggregate_Data" *Dict*
   -> "MCMC_Calc"  *DataFrame*  MCMC Uncertainty Inputs, values copied from Merged_Peaks
   -> "MCMC_Data" *DataFrame*, columns of sigma_exp[n] and phase_mu[n] for n phases MCMC Distribution Data (8000 normalized intensities)
   -> "MCMC_Result_Number" *DataFrame* columns for each phase, with estimated phase fraction by number of unit cells
   -> "MCMC_Result_Mass" *DataFrame* columns for each phase, with estimated phase fraction by mass of unit cells
   -> "MCMC_Result_Volume" *DataFrame* columns for each phase, with estimated phase fraction by volume of unit cells
   -> "Uncert_Source_Summary" *DataFrame* rows for each phase, with aggregate uncertainties
   -> "Phase_Fraction_Result_Number" *DataFrame* rows for each phase
   -> "Phase_Fraction_Result_Mass" *DataFrame* rows for each phase
   -> "Phase_Fraction_Result_Volume" *DataFrame* rows for each phase



   -> Phase Fraction Data (8000 n_ints run through phase frac calc)
   -> Peak (row)
    |
    -> "Le_Bail_Peaks"	*DataFrame*	(LeBail Fit values, uncertainties[where?])
    -> "Theoretical_Intensities" *DataFrame*
    -> t_peaks *Dataframe* 		(hist peak list from peak fit algorithm)
    -> "Merged_Peaks" *DataFrame*	(merge of hist peak list, theoretical intensities, Le Bail peaks)

    -> Peak Fit (values, uncertainties)
    -> Gaussian Fit (values, uncertainties)
    -> 
    -> hkl, multiplicity
    -> Phase
    -> "Interaction_Calc"  *DataFrame* interaction data by peak
       ( to assemble interaction volume plots)
    -> "Interaction_Plots"

### Possible issue with phase names.  Sometimes from cif file name with extension, and sometimes from name given inside cif file...

Mutability
	dictionaries and DataFrames should be mutable, so you don't need to pass the object back from a function

	-> Flags doesn't work this way, needed to pass them back...


Flags syntax:

        value: numeric value (float) of flagged value
        source: short string text explaining the what step in the data is flagged
        flag: longer string text describing the alert to user
        suggestion: string text with suggestions on source or mitigation methods to decrease error