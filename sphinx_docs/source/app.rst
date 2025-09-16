app
===============

*****************************************
Documentation for app.py
*****************************************
This is the main file for dash and plotly


=========================
main_dict
=========================

ONLY CHECKED EXAMPLE05, SINGLE DATAFILE
Majority of data is stored in a dictionary that has the following keys:

- results_table: Nested dictionary with type dictionary dataset (Dataset: 1), type tuple index (always zero? - seems to have a duplicate empty row), type list for each peak (sorted by two theta), type dictionary with theoretical and fit data (keys: 'pos_fit', 'int_fit', 'sig_fit', 'gam_fit', 'Peak_Fit_Success', 'u_pos_fit', 'u_int_fit', 'back_int_bound', 'signal_to_noise', 'u_int_count', 'rel_int_fit', 'rel_int_count', 'h', 'k', 'l', 'mul', 'two_theta', 'F_calc_sq', 'I_corr', 'R_calc', 'Phase', 'n_int', 'pos_diff', 'sample_index').
- phase_frac: Nested dictionary with type dictionary dataset (Dataset: 1), type tuple index (always zero? - seems to have a duplicate empty row), type list for each phase, type dictionary with phase fractions (number of cells) and normalized intensity data (keys: 'Phase', 'Phase_Fraction', 'Phase_Fraction_StDev', 'Number_hkls', 'hkls', 'Mean_nint', 'StDev_nint')
- volume_conversion: Nested dictionary with type dictionary dataset (Dataset: 1), type tuple index (always zero? - seems to have a duplicate empty row), type list for each phase, type dictionary with phase fractions (volume of cells) and normalized intensity data (keys: 'Phase', 'Phase_Fraction', 'Phase_Fraction_StDev', 'Number_hkls', 'hkls', 'Mean_nint', 'StDev_nint')
- mass_conversion: Nested dictionary with type dictionary dataset (Dataset: 1), type tuple index (always zero? - seems to have a duplicate empty row), type list for each phase, type dictionary with phase fractions (mass of cells) and normalized intensity data (keys: 'Phase', 'Phase_Fraction', 'Phase_Fraction_StDev', 'Number_hkls', 'hkls', 'Mean_nint', 'StDev_nint')
- two_thetas: Nested dictionary with type dictionary dataset (Dataset: 1), type list with two theta values for range of data imported.  Used as x-axis data
- ti_tables: Nested dictionary with type dictionary dataset (Dataset: 1),type tuple index (always zero? - seems to have a duplicate empty row), type list for each peak (sorted by two theta), type dictionary with theoretical intensity data (keys: 'h', 'k', 'l', 'mul', 'two_theta', 'F_calc_sq', 'I_corr', 'R_calc', 'Phase')
- uncert: Nested dictionary with type dictionary dataset (Dataset: 1), type tuple index (always zero? - seems to have a duplicate empty row), type list for suggestions or flags, type dictionary with suggestion (keys: 'Value', 'Source', 'Flags', 'Suggestions') RENAME
- altered_results: similar to results table, after unit change?
- altered_phase: similar to phase_frac table, after unit change?
- altered_ti: ? not clear why this would change
- fit_points:  Nested dictionary with type dictionary dataset (Dataset: 1),type list with histogram data [0] fit to background [1] and fit to the data [2], type list with data values for range of data imported. Used as y-axis data.
- interaction_vol_data: Nested dictionary with type dictionary (each phase), type list for each peak, type list for path data [0] and scattering data [1], type tuple index (always zero? - seems to have a duplicate empty row), type list for points along the interaction path (25 points typical), type dictionary with the intensity data (keys: ['x', 'y', 'length', 'I']) ODD THAT THERE'S TWO DATA STRUCTURES IN THE MIDDLE
- cell_masses: Dictionary for each phase with the mass value determined from the element proportions
- cell_volumes: Dictionary for each phase with the volume value determined from the element proportions
- cell_mass_vec: List for each phase with the mass value determined from the element proportions. Order matches dictionary order.
- cell_volume_vec: List for each phase with the volume value determined from the element proportions. Order matches dictionary order.
- mu_samps: Nested dictionary with type dictionary (each phase? listed as phase_mu[n] n=1,2), list of length 8000 (?!?).  Maybe for MCMC?
- crystallites: Nested dictionary with type dictionary (each phase), list for each peak, type list with diffracting data (list: ?, number illuminated, fraction illuminated, number diffracting)


*****************************************
Functions and docstrings
*****************************************

.. automodule:: app
    :members:


