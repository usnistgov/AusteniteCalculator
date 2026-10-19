overview

******************************
Application Overview
******************************

The application loads as a single webpage with 9 separate tabs.  The default tab is the 'Data Upload' tab.  For examples see the :doc:`user_guide`

==============================
About
==============================

The 'About' tab provides a table with the 'Version Summary' for the application, and a link to the Manual and User Guide.  The version data contains information about the Austenite Calculator release and git history, as well as the GSAS version

==============================
Data Upload
==============================

The 'Data Upload' tab is the first page that loads for the Austenite Calculator.  There are 3 steps to follow on this page before pressing the 'Submit' button to run the calculation.

1. Choose to 'Upload Custom Files' or 'Use Example Files'.
2. Choose the 'Number of Initial MCMC Samples'.
3. Press the 'Submit' button.

If you choose to 'Upload Custom Files', the 'X-Ray diffraction File' that you choose must be compatible with GSAS-II importers. The 'Instrument Parameter File' should also follow the GSAS-II convention and construction.  **Under development - the abililty to create an instrument parameter file on the 'File Creation' tab**  'Crystallographic Information Files' will need to be provided for each phase to be analyzed.  A 'Crystallites Illuminated JSON' file will also need to be provided.  The 'File Creation' tab walks through the values required and will create a file for download if needed.

If you are uploading multiple files and want to sum the data together (i.e. to sum over several orientations), check the 'Sum Individual Files?' box.

The 'Use Example Files' option allows one to explore the application results by providing the requisite datafiles.  'Example 01' is for a single sample (datafile), 'Example 02' demonstrates the application for multiple samples (datafiles).

For the 'Statistical Inference Options', this sets the number of Markov Chain Monte Carlo (MCMC) runs that are used intially.  The total number of runs used in the sampling is fixed at 8000.

After pressing the 'Submit' button, a running icon and text "Running Submission... Please wait while results are computed... " will appear. After the application completes additional data will be filled in on the rest of the tabs. If no data shows up, check the 'Error Log' tab. Refresh the webpage to reset the application before uploading different files or running an additional example.

==============================
Intensity Plots
==============================

After the application completes, two intensity vs Two Theta plots will appear below the 'Raw and Fitted Diffraction Data' section.  The left plot shows the raw data, and the right plot shows the fits superimposed on the raw data. For each plot you can zoom, pan, select and/or save the image. The 'Which Dataset' pulldown menu allows selection of each dataset uploaded and analyzed.

Below the plots in the 'Notes for User on Austenite Calculation' section, a table of flagged values and notes will be provided.  These provide values found during the fitting and/or suggestions to explore.


==============================
Normalized Intensity
==============================

On the 'Normalized Intensity' tab, there are three sections for one plot and two tables: 'Normalized Intensities per Peak Plot', 'Fit Values per Peak Summary Table' and 'Calculated Theoretical Intensities per Peak'. The 'Which Dataset' pulldown menu allows selection of each dataset uploaded and analyzed.

The 'Normalized Intensities per Peak Plot' shows the measured intensity divided by the theoretical intensity for each peak. The markers and lines are color coded by the phase each peak belongs to.  Markers show the value per peak, and the horizontal lines show the mean value.  Icons and lines are different for each type of fitting.  Ideally the normalized intensity should be constant per phase, but in practice this is often not the case.

The 'Fit Values per Peak Summary Table' contains a fit parameters for each peak.  Prefixes and suffixes are common in this table. Prefixes include: 'pos' indicates Two Theta position in degrees, 'int' intensity value in x-ray counts, 'sig' is the Gaussian component fit value, 'gam' is the Lorentzian component fit value.  Suffixes 'LB' stands for Le Bail fit, 'fit' stands for individual peak fit, 'G' is for Gaussian only fit, and 'TR' for trapizoidal rule integration of the peak.  Additional suffixes 'bg' is for a background value, and 'total' for the total counts of the peak including background.

Table 'Calculated Theoretical Intensities per Peak' provides data for the theoretical intensities to permit comparison with other sources.

==============================
Phase Fraction
==============================

On the 'Phase Fraction' tab, there are three tables and a histogram.  As noted in the :doc:`user_guide`, there are several ways to express phase fractions. Select from 'Number of Unit Cells', 'Mass Fraction', and 'Volume Fraction' to update the histogram and value table. Use 'Which Dataset' pulldown menu to select each dataset.

The table 'Phase Fraction Values (select units)' and plot 'Phase Fraction Histogram (select units)' summarize the phase fraction values. The histogram plot shows the phase fraction values from the 8000 MCMC runs.  Mean and median values for each phase are shown, as are approximations of the 1 sigma and 2 sigma bounds on either side of the distribution, taken from quantiles 0.1587 and 0.8413 for 1 sigma and 0.02275 and 0.97725 for 2 sigma.


Two additional tables 'Sources of Uncertainty (scaled by normalized intensity)' and 'Sources of Uncertainty (per peak, Exponential Notation)' are shown below the plot. Table 'Sources of Uncertainty (scaled by normalized intensity)' has columns:
* 'Mean_n_int_fit' - the mean value for the normalized intensity as shown in the 'Normalized Intensity' tab
* 'Median_phase_mu' - median value for the normalized intensity from the MCMC calculation.  This should be close to the 'Mean_n_int_fit' value.
* 'Median_sigma_exp' - median value of the      Median_n_u_count_fit     Median_n_u_int_fit     Median_n_u_N_Diffracting_95pct

scales the sources of uncertainty to the median phase






==============================
Crystallites Illuminated
==============================


==============================
File Creation
==============================


==============================
Error Log
==============================


==============================
Download Results
==============================
