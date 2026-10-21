overview

******************************
Application Overview
******************************

The application loads as a single webpage with 9 separate tabs.  The default tab is the 'Data Upload' tab.  For examples see the :doc:`user_guide`.  Many of the tabs will have blank placeholders until the application runs.

==============================
About
==============================

The 'About' tab provides a table with the 'Version Summary' for the application, and a link to the 'Manual and User Guide'.  The 'Version Summary' table contains information about the Austenite Calculator release and git history, as well as the GSAS version.  This is mainly provided for diagnostics and consistency check.

==============================
Data Upload
==============================

The 'Data Upload' tab is the first page that loads for the Austenite Calculator.  There are 3 steps to follow on this page before results will display.

1. 'Data Selection' - choose option 1 to 'Upload Custom Files' or option 2 'Use Example Files'.
2. Choose the 'Number of Initial MCMC Samples'.
3. Press the 'Submit' button.

If you choose to 'Upload Custom Files', the 'X-Ray diffraction File' that you choose must be compatible with GSAS-II importers. The 'Instrument Parameter File' should also follow the GSAS-II convention and construction.  **Under development - the ability to create an instrument parameter file on the 'File Creation' tab**  'Crystallographic Information Files' will need to be provided for each phase to be analyzed.  A 'Crystallites Illuminated JSON' file will also need to be provided.  The 'File Creation' tab walks through the values required and will create a file for download if needed.

If you are uploading multiple files and want to sum the data together (i.e. to sum over several orientations), check the 'Sum Individual Files?' box.

The 'Use Example Files' option allows one to explore the application results by providing the requisite datafiles.  'Example 01' uses a single sample (datafile), 'Example 02' demonstrates the application for multiple samples (datafiles).

For the 'Statistical Inference Options', this sets the number of Markov Chain Monte Carlo (MCMC) runs that are used initially.  The total number of runs used in the sampling and phase fraction calculation is fixed at 8000.

After pressing the 'Submit' button, a running icon and text "Running Submission... Please wait while results are computed... " will appear. After the application completes additional this message with disappeear, data will be filled in on the rest of the tabs, and the application should switch to the 'Intensity Plots' tab. If no data shows up, check the 'Error Log' tab.

Refresh the webpage to reset the application before uploading different files or running an additional example.

==============================
Intensity Plots
==============================

After the application completes, two Intensity vs Two Theta plots will appear below the 'Raw and Fitted Diffraction Data' section.  The left plot shows the raw data, and the right plot shows the individual peak fit ('Peak fit') and Le Bail fit (Le Bail fit) superimposed on the raw data. For each plot you can zoom, pan, select and/or save the image. The 'Which Dataset' pulldown menu allows selection of each 'dataset_#' uploaded and analyzed when multiple samples are used, following the order uploaded or selected.

Below the plots in the 'Notes for User on Austenite Calculation' section, a table of flagged values and notes will be provided.  These provide values (and units) found during the fitting, where in the analysis they were noted (source), a descriptive flag (flags) and suggestions for the user to explore and consider.


==============================
Normalized Intensity
==============================

On the 'Normalized Intensity' tab, there are three sections.  From top to bottom these are for one plot and two tables: 'Normalized Intensities per Peak Plot', 'Fit Values per Peak Summary Table' and 'Calculated Theoretical Intensities per Peak'. The 'Which Dataset' pulldown menu allows selection of each dataset uploaded and analyzed.

The 'Normalized Intensities per Peak Plot' shows the measured intensity divided by the theoretical intensity for each peak. The markers and lines are color coded by the phase each peak belongs to.  Markers show the value per peak, and the horizontal lines show the mean value.  Icons and lines are different for each type of fitting.  Ideally the normalized intensity should be constant per phase, but in practice this is often not the case.

The 'Fit Values per Peak Summary Table' contains a fit parameters for each peak.  Prefixes and suffixes are common to this table and several others. Prefixes include: 'pos' which indicates Two Theta position in degrees, 'int' which is the intensity value in x-ray counts, 'sig' is the Gaussian component of the fit value, 'gam' is the Lorentzian component fit value.  Suffixes 'LB' stands for Le Bail fit, 'fit' stands for individual peak fit, 'G' is for Gaussian only fit, and 'TR' for trapezoidal rule integration of the peak.  Additional suffixes 'bg' is for a background value, and 'total' for the total counts of the peak including background.

Table 'Calculated Theoretical Intensities per Peak' provides data for the theoretical intensities to permit comparison with other sources and boolean flags used to determine success of the peak fit.

==============================
Phase Fraction
==============================

On the 'Phase Fraction' tab, there are three tables and a histogram.  As noted in the :doc:`user_guide`, there are several ways to express phase fractions. Select from 'Number of Unit Cells', 'Mass Fraction', and 'Volume Fraction' to update the histogram and value table. Use 'Which Dataset' pulldown menu to select each dataset.

The table 'Phase Fraction Values (select units)' and plot 'Phase Fraction Histogram (select units)' summarize the phase fraction values. The histogram plot shows the phase fraction values from the 8000 MCMC runs.  Mean and median values for each phase are shown, as are approximations of the 1 sigma and 2 sigma bounds on either side ('Neg' - closer to 0 or 'Pos' - closer to 1) of the distribution, taken from quantiles 0.1587 and 0.8413 for 1 sigma and 0.02275 and 0.97725 for 2 sigma.

Two additional tables 'Sources of Uncertainty (scaled by normalized intensity)' and 'Sources of Uncertainty (per peak, scaled by normalized intensity)' are shown below the plot. Table 'Sources of Uncertainty (scaled by normalized intensity)' has columns:

* 'Mean_n_int_fit' - the mean value for the normalized intensity as shown in the 'Normalized Intensity' tab.
* 'Median_phase_mu' - median value for the normalized intensity from the MCMC calculation.  This should be close to the 'Mean_n_int_fit' value.
* 'Median_sigma_sample' (multiple samples only) - median value of the uncertainty between samples when multiple samples were analyzed
* 'Median_sigma_exp' - median value of the uncertainty in normalized intensity between all peaks of each phase.
* 'Median_n_u_count_fit' - median value of the uncertainty in counts based on the number of intensity counts reported the individual peak fit
* 'Median_n_u_int_fit' - median value of the uncertainty in fit of intensity value reported during the individual peak fit.
* 'Median_n_u_N_Diffracting_95pct' - median value of the uncertainty based on the number of crystallites diffracting.

.. note::
    The largest values between the 4 (or 5 for multiple samples) columns of uncertainty metrics are the sources of uncertainty that are dominating the phase fraction uncertainty.


The table 'Sources of Uncertainty (per peak, scaled by normalized intensity)' shows the uncertainties calculated for each peak (when available).  The left side of the table shows uncertainties in position and intensity for the individual peak fit (_fit) and Le Bail (_LB) fits. The right side of the table shows the uncertainty based on the counts (_count_), the fitting of the intensity value (_int_), and number of crystallites diffracting at the 95% depth. (_N_Diffracting_95pct_).

.. note::
    Each of the values in this table are different for each peak, but only the median value for each phase is used for the phase fraction uncertainty. If there are significant outliers in the values for a particular peak, the uncertainty may be underestimated.


==============================
Crystallites Illuminated
==============================

On the 'Crystallites Illuminated' tab, there is one table and two plots. Use 'Which Dataset' pulldown menu to select each dataset. Below the 'Interaction Volume Table' there's a second pulldown menu 'Select Peak Index' to select a particular peak for the two plots: 'Z Depth Histogram Plot' and 'Incident Angle Plot'.  The majority of this data is calculated based on the provided 'Crystallites Illuminated JSON (.json)' file.

The 'Interaction Volume Table' lists the peaks in the analysis range in increasing order of two theta by phase and hkl.  The peak index used in 'Select Peak Index' is shown on the left and right of the table.

Working from right to left, the column '95pct_Escaped_Depth_um' lists the estimated maximum distance into the material where 95% of the x-rays that have diffracted and escaped the reach the sample surface (not absorbed after diffracting).  The 95% depth is likely an upper bound for the maximum depth. Column 'l_bar_um' is the 'mean lineal intercept length' in micrometers per ASTM E112 through a spherical particle, and 'Powder_Size_um' is the diameter of a sphere either representing a mean grain size or powder size.

Returning to the right side of the table, comparison of the 'l_bar_um' and '95pct_Escaped_Depth_um' determines the number of layers 'N_Layers_95pct' that are illuminated.  Details included in the 'Crystallites Illuminated JSON (.json)' file set the area that is illuminated, and based on these area values, the 'N_Layers_95pct', 'Powder_Size_um', and preliminary values for the phase fraction determine the number of crystallites illuminated 'N_illuminated_95pct'.  Further information in the 'Crystallites Illuminated JSON (.json)' file determine the fraction of grains that are likely to be in the diffraction condition 'Diffracting_Fraction', which then sets the number of grains diffracting 'N_Diffracting_95pct'.  Uncertainties used in 'n_u_N_Diffracting_95pct' are based on the Poisson's count uncertainty of 'N_Diffracting_95pct' and scaled by the normalized intensity value.

 The 'Z Depth Histogram Plot' shows a histogram of the escaped x-rays and provides lines for the 95%, 68%, and 50% depths. A schematic 'Incident Angle Plot' is shown to illustrate the directions of the incident, diffracting, and penetrating x-rays.  As the peak is varied, the geometry changes based on the two theta, to show why some of the values of the 'Interaction Volume Table' will vary as a function of hkl.

==============================
File Creation
==============================

This tab has sections 'Crystallites Illuminated JSON File Creation' and 'Instrument Parameter File Creation'  In 'Crystallites Illuminated JSON File Creation', there's 11 boxes of data to enter with the relevant parameters from the particular sample and diffraction system used. A description of the values needed for each box is listed on this tab for reference.

While it may not be possible to know exact values for each of these, :doc:`CrystallitesIlluminatedFileCreation` provides expanded discussion and possible bounding values.  Also use the column 'n_u_N_Diffracting_95pct' from the table 'Sources of Uncertainty (per peak, scaled by normalized intensity)' to assess how critical the number of diffracting crystallites are to the uncertainty calculation and determine the level of effort necessary to get these values (i.e. if assumptions that limit the number diffracting crystallites still result in insignificant sources of uncertainty, no further effort is likely required)

There is an additional section 'Instrument Parameter File Creation', but this is not currently supported in this release.  For now, use the GSAS-II tutorials if needed ( https://advancedphotonsource.github.io/GSAS-II-tutorials/tutorials.html) such as (https://advancedphotonsource.github.io/GSAS-II-tutorials/CWInstDemo/FindProfParamCW.html).  As noted in the tutorial "Ideally, one should use a material or mixture of materials that has peaks over the entire range where you collect data and use material(s) that have negligible sample broadening (from crystallite size or microstrain)."

==============================
Error Log
==============================

This tab has sections 'Error log' and 'Server Log'.  If the code executes properly, 'Error log' should be blank.  If not, the error log may have useful hints on what went wrong.  If you are unable to solve the issue, contact the developers for assistance.  Copies of the log and files are most helpful to reproduce the issue.  Similarly, the 'Server Log' is mainly included for diagnostics.

==============================
Download Results
==============================

This tab has a button 'Download Results' to save the complete analysis results.  The file is .zip file that contains several python 'pickle' files as a storage container.
