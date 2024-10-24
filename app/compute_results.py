from bdb import Breakpoint
from cProfile import label
from enum import unique
#from tkinter import TRUE  #doesn't seem to be used, and causes errors in sphinx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
import fit
import os
import atmdata
from copy import deepcopy
import json
import base64
import re

from interaction_vol import crystallites_illuminated_calc, findMu, getFormFactors, create_graph_data
from compute_uncertainties import run_stan, generate_param_table

def compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,xtal_data,G2sc):
    """

    Main computation function for phase calculations
    *ADD MORE ON WHAT IT DOES*
    
    
    Parameters:
        datadir: Location data is stored
        workdir: Working directory for data
        xrdml_fname: Diffraction data (xrdml title legacy)
        instprm_fname: Instrument Parameter File
        cif_fnames: Crystollographic Info File
        xtal_data: crystal data from json file
        G2sc: GSAS-II Scripting Toolkit location
    
    Returns:
        | A tuple that contains the following items
        | **fit_data** a list of lists with the histogram data, fit of the background, and fit of the data;
        | **DF_merged_fit_theo** a pandas DataFrame with collected fit and theoretical intensities ;
        | **DF_phase_fraction** a pandas DataFrame with phase fraction ;
        | **two_theta** a python list (?) with the two_theta data from the GSAS-II histogram ;
        | **tis** a pandas DataFrame with the theoretical intensities;
        | **DF_flags_for_user** a pandas DataFrame with the flags and notes to the user
    
    """
    
    #Helper functions to create full path descriptions
    data_path_wrap = lambda fil: datadir + '/' + fil
    save_wrap = lambda fil: workdir + '/' + fil
    
    # start new GSAS-II project
    gpx = G2sc.G2Project(newgpx=save_wrap('pkfit.gpx'))

    #initialize Uncertainty DataFrame
    DF_flags_for_user=flag_phase_fraction(np.nan, " ", "Initialize", " ")

    #############################
    # Read in diffraction data
    #############################
    print("\n\n Read in diffraction data\n")
    
    # read in diffraction data as a powder histogram
    # Do this first to get the two_theta range
    hist = gpx.add_powder_histogram(data_path_wrap(xrdml_fname),
                                    data_path_wrap(instprm_fname),
                                    databank=1, instbank=1)

    # Get the two_theta range of the histogram
    two_theta_range=hist.getdata('X')
    min_two_theta=min(two_theta_range)
    max_two_theta=max(two_theta_range)
    #print(min_two_theta,max_two_theta)

    ########################################
    # Caculate the theoretical intensities from cif files
    ########################################
    print("\n\n Calculate Theoretical Intensities\n")

    tis = {} # e.g. tis['austenite-duplex.cif'] maps to austenite theoretical intensities

    for i in range(len(cif_fnames)):
        tis[cif_fnames[i]] = get_theoretical_intensities(gpx_file_name=cif_fnames[i] + '.gpx', \
                                                         material=cif_fnames[i], \
                                                         cif_file=cif_fnames[i], \
                                                         instrument_calibration_file=instprm_fname, \
                                                         xtal_data=xtal_data, \
                                                         G2sc=G2sc, \
                                                         x_range=[min_two_theta,max_two_theta], \
                                                         DataPathWrap=data_path_wrap, \
                                                         SaveWrap=save_wrap, \
                                                         DF_flags_for_user=DF_flags_for_user)

    # Merge and sort the theoretical intensities
    #? Sort seems a kind of fragile way to align the data 
    tis = pd.concat(list(tis.values()),axis=0,ignore_index=True)
    tis = tis.sort_values(by='two_theta')
    tis = tis.reset_index(drop=True)
    print("\n\n Theoretical Intensity Dataframe")
    print(tis)

    ########################################
    # Read in phase data
    ########################################
    print("\n\n Read in Phase Data\n")

    phases = {}
    a0 = {}
    for i in range(len(cif_fnames)):
        phases[cif_fnames[i]] = get_phase(data_path_wrap(cif_fnames[i]), cif_fnames[i], gpx) # phase data
        a0[cif_fnames[i]] = phases[cif_fnames[i]].data['General']['Cell'][1] # lattice parameter

    # Find the ka1 wavelength in the file
    # works for some data files that have information encode, otherwise may need to prompt
    if 'Lam1' in hist.data['Instrument Parameters'][0]:
        Ka1_wavelength=hist.data['Instrument Parameters'][0]['Lam1'][0]
        print("using the Lam1 value, multiple wavelengths")
    elif 'Lam' in hist.data['Instrument Parameters'][0]:
        Ka1_wavelength=hist.data['Instrument Parameters'][0]['Lam'][0]
        print("using the Lam value, single wavelength")
    else:
        Ka1_wavelength=1.5405
        DF_flags_for_user=flag_phase_fraction(0,"Histogram Data", "Assumed Cu single wavelength", "Check input file", DF_to_append=DF_flags_for_user)
        print("No wavelength found, defaulting to Cu")

    #breakpoint()
    
    ########################################
    # use the theoretical intensities for peak fit location
    ########################################
    print("\n\n Peak Fit (LeBail) of Experimental Data \n")

    # use the theoretical intensities for peak fit location
    peaks_list=tis['two_theta']
    
    # Add to the two_theta values to move the peak location for debugging
    # 0.2 on example 5 is enough to throw off the last two peaks
    # 0.5 on example 5 will result in negative intensities being fit
    # tis['two_theta']+= 0.5
    #peaks_list=tis['two_theta']+0.5

    peaks_ok = False
    fit_attempts = 0
    fit_attempt_limit = 3
    peak_verify = []
    t_peaks = 0
    t_sigma = 0
    t_gamma = 0
    t_int = 0
    t_pos = 0

    while not (peaks_ok):
        print("\n\n Fit attempt number ", fit_attempts," \n")
        if(fit_attempts == 0):
            fit.fit_peaks(hist, peaks_list)
        # Currently the fit processes are a little different...
        elif(fit_attempts == 1):
            fit.fit_moved_right_peaks(hist, peaks_list, peak_verify)
            DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Moving initial fit location to a lower 2-theta value", "Adjust lattice spacing in .cif files", DF_to_append=DF_flags_for_user)
        elif(fit_attempts == 2):
            fit.fit_moved_left_peaks(hist, peaks_list, peak_verify)
            DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Moving initial fit location to a higher 2-theta value", "Adjust lattice spacing in .cif files", DF_to_append=DF_flags_for_user)
        elif(fit_attempts == 3):
            holding_sig = False
            holding_gam = True
            for x in range(6):
                if not(np.all(peak_verify == True)):
                    if holding_gam:
                        fit.fit_peaks_holdgam(hist, peaks_list, Chebyschev_coeffiecients, peak_verify)
                        holding_gam = False
                        holding_sig = True
                    elif holding_sig:
                        fit.fit_peaks_holdsig(hist, peaks_list, Chebyschev_coeffiecients, peak_verify)
                        holding_sig = False
                        holding_gam = True
            t_peaks = pd.DataFrame(hist.data['Peak List']['peaks'])
            t_sigma = t_peaks.iloc[:,4]
            t_gamma = t_peaks.iloc[:,6]
            t_int = t_peaks.iloc[:,2]
            t_pos = t_peaks.iloc[:,0]
            peak_verify = fit.create_verify_list(t_pos, t_int, t_sigma, t_gamma)

        t_peaks = pd.DataFrame(hist.data['Peak List']['peaks'])
        t_sigma = t_peaks.iloc[:,4]
        t_gamma = t_peaks.iloc[:,6]
        t_int = t_peaks.iloc[:,2]
        t_pos = t_peaks.iloc[:,0]

        peak_verify = fit.create_verify_list(t_pos, t_int, t_sigma, t_gamma)

        fit_attempts += 1

        if(np.all(peak_verify == True)):
            print("\n\n All values are within a likeable range \n")
            
            # Print out some of the goodness of fit data
            try:
                print("\n\n Goodness of fit value: ", hist.data['Peak Fit Rvals']['GOF'])
                DF_flags_for_user=flag_phase_fraction(hist.data['Peak Fit Rvals']['GOF'],"Fitting", "Fitting Goodness of Fit (GOF)", "--ADD Guidance--", DF_to_append=DF_flags_for_user)
            except:
                print("Error creating Goodness of fit")
                DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Missing Goodness of Fit (GOF) Value", "Missing bits of code in GSAS-II", DF_to_append=DF_flags_for_user)                
            peaks_ok = True
        
        elif(fit_attempts >= fit_attempt_limit):
            print("\n\n Intensities and Positions are NOT all positive, HOWEVER iteration limit reached \n")
            peaks_ok = True
            DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Limit of Fitting attempts reached", "Adjust lattice spacing in .cif files", DF_to_append=DF_flags_for_user)
            
        else:
            print("\n\n Intensities and Positions are NOT all positive, retrying \n")
            peaks_ok = False
            DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Intensities and Positions are NOT all positive, retrying", "Retrying fitting" , DF_to_append=DF_flags_for_user)
            # reset the peak list in the histogram to avoid appending during successive attempts
            hist.data['Peak List']['peaks']=[]
            # reset and repopulate the peak list
            peaks_list=tis['two_theta']


    two_theta = hist.data['data'][1][0]
    h_data = hist.data['data'][1][1]
    h_background = hist.data['data'][1][4]
    h_fit = hist.data['data'][1][3]

    #? Also fit the lortenzian (gam) component?
    #? There's a way to keep the fit sig values, instead of having them reset to the instrument parameter

    ########################################
    # Merge experimental and theoretical data
    ########################################
    print("\n\n Create dataframe from fit data \n")

    # Extract information from the peak fits.
    #? Similarly, sort here seems like a fragile way to align the data.
    DF_merged_fit_theo = pd.DataFrame(hist.data['Peak List']['peaks'])
    DF_merged_fit_theo = DF_merged_fit_theo.iloc[:,[0,2,4,6]]
    DF_merged_fit_theo.columns = ['pos_fit','int_fit','sig_fit','gam_fit']
    
    DF_merged_fit_theo["Peak_Fit_Success"]= peak_verify
    DF_merged_fit_theo["Peak_Fit_Success"] = DF_merged_fit_theo["Peak_Fit_Success"].astype('bool')
    
    ##### Extract uncertainties from the fitting process
    u_pos_fit_list=[]
    u_int_fit_list=[]
    for i in list(range(len(DF_merged_fit_theo.index))):
        u_pos_fit_list.append(hist.data['Peak List']['sigDict']['pos'+str(i)])
        u_int_fit_list.append(hist.data['Peak List']['sigDict']['int'+str(i)])

    DF_merged_fit_theo['u_pos_fit']=u_pos_fit_list
    DF_merged_fit_theo['u_int_fit']=u_int_fit_list

    ##### calculate uncertainty based on counting statistics (square root of counts for Poisson process)
    DF_merged_fit_theo=fit.fit_background(DF_merged_fit_theo,hist, peaks_list)
    
    # p 362 Klug & Alexander "X-Ray Diffraction proceedures"
    DF_merged_fit_theo['u_int_count']=(DF_merged_fit_theo['back_int_bound']+DF_merged_fit_theo['int_fit'])**0.5
    
    #DF_merged_fit_theo['u_int_count']=DF_merged_fit_theo['int_fit']**0.5

    DF_merged_fit_theo = DF_merged_fit_theo.sort_values('pos_fit')
    DF_merged_fit_theo = DF_merged_fit_theo.reset_index(drop=True)

    ##### add relative uncertainties.  Maybe cut later, but diagnostic for now
    DF_merged_fit_theo['rel_int_fit']=DF_merged_fit_theo['u_int_fit']/DF_merged_fit_theo['int_fit']
    DF_merged_fit_theo['rel_int_count']=DF_merged_fit_theo['u_int_count']/DF_merged_fit_theo['int_fit']

    #DF_merged_fit_theo = DF_merged_fit_theo.loc[(0 < DF_merged_fit_theo.sig) & (DF_merged_fit_theo.sig < 90),:]

    # Merge the theoretical and experimental peak values
    # Uses the sorting for alignment of rows.  Likely a better way and/or error checking needed
    #? Should the if/else be a try/except block?
    print("\n\n Concatenating Dataframes\n")
    DF_merged_fit_theo = pd.concat((DF_merged_fit_theo,tis),axis=1)
    DF_merged_fit_theo = DF_merged_fit_theo
    DF_merged_fit_theo['n_int'] = (DF_merged_fit_theo['int_fit']/ \
                                   (DF_merged_fit_theo['Texture Correction']* \
                                   DF_merged_fit_theo['R_calc']))

    DF_merged_fit_theo['pos_diff'] = DF_merged_fit_theo['pos_fit']-DF_merged_fit_theo['two_theta']

    ########################################
    # Calculate the phase fraction
    ########################################
    print("\n\n Calculating Phase Fraction\n")
    DF_phase_fraction,  DF_flags_for_user = calculate_phase_fraction(DF_merged_fit_theo, DF_flags_for_user)

    print("\n\n Before fit data\n")
    fit_data = [h_data.tolist(), h_background.tolist(), h_fit.tolist()]
    print("\n\n After fit data\n")

   #return a bunch of data in dataframes, plots are created dynamically
    return (fit_data, 
            DF_merged_fit_theo,   
            DF_phase_fraction,
            two_theta,
            tis,
            DF_flags_for_user)

#####################################
######### Plotting Fuctions #########
#####################################

#####################################
def df_to_dict(df):
    """
    Function for converting a pandas dataframe to a python dictionary. Need a dictionary for dash data_table

    Args:
        df: pandas Dataframe

    Returns:
        | Two dictionaries
        | **out_dict** a dictionary of the pandas dataframe;
        | **out_columns** a dictonary with the column name and position
    """
    out_dict = df.to_dict('records')
    out_columns = [{"name": i, "id": i} for i in df.columns]

    return out_dict, out_columns

#####################################
def get_figures(hist):
    """
    Plot the intensity vs. two_theta data from a GSAS-II diffraction histogram
    
    Args:
        hist: GSAS-II powder histogram
    
    Returns:
        **fig** Plotly Express Figure
    """
    df = pd.DataFrame({
        "two_theta":hist.data['data'][1][0],
        "intensity":hist.data['data'][1][1]
    })

    fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')
    return fig

def get_pf_uncertainty_fig(pf_uncertainties): 
    """
    *NEEDS DOCSTRING*
    
    Args:
        pf_uncertainties: ???
    
    Returns:
        **pf_uncertainty_fig** ???
    """

    pf_uncertainty_fig = px.histogram(pf_uncertainties['mu_df'],x='value',color='which_phase',opacity=.7,barmode='overlay',histnorm='probability density')

    unique_phases = pf_uncertainties['unique_phase_names']
    for ii in range(len(unique_phases)):
        t_vals = pf_uncertainties['mu_df'].loc[ pf_uncertainties['mu_df'].which_phase == unique_phases[ii]  ,'value']
        pf_uncertainty_fig.add_vline(np.quantile(t_vals,.5))
        pf_uncertainty_fig.add_vline(np.quantile(t_vals,.025),line_dash='dot')
        pf_uncertainty_fig.add_vline(np.quantile(t_vals,.975),line_dash='dot')

    return pf_uncertainty_fig

#####################################
def two_theta_compare_figure(Merged_DataFrame):
    """
    Plot the difference between fitted vs. theoretical two_theta data
    Nominally this difference should be near zero, outlier values may indicate poor fit.  Trends may indicatate errors in theoretical values
    
    Args:
        Merged_DataFrame: Dataframe after merging with fitted and theoretical intensities
    
    Returns:
        **fig** Plotly Express Figure
    """
    
    fig = px.scatter(Merged_DataFrame, x="two_theta", y="pos_diff", color="Phase",
                    labels = {
                        'pos_fit':'Diffference between fit and theoretical 2-theta',
                        'two_theta':'two theta value'
                        }
                    )
    
    return fig



#####################################
########## Helper Fuctions ##########
#####################################

#####################################
def get_phase(cif_wrap, phase_name, project):
    """
    Retreieve the phase information from file.  Assumes phase information is stored in a .cif file with format hint (fmthint)
    *LIKELY NEEDS AN EXCEPT BLOCK*
    
    Args:
        cif_wrap: path to file
        phase_name: Name for the phase
        project: GSAS-II project file to add phase to
    
    Returns:
        **project** GSAS-II project file with phase data wrapped in
    """
    return project.add_phase(cif_wrap, phase_name, fmthint = 'CIF')

#####################################
def find_sin_thetas(phase_lattice_parameter, hkl_list, wavelength):
    """

    Calculate the position in two theta for a list of hkls.  Used to mark locations for fitting
    *!!! Have only tested cubic crystal symmetry with widely spaced peaks !!!*
    
    Args:
        phase_lattice_parameter: lattice parameter
        hkl_list: list of lattice planes (hkl)
        wavelength: dominant wavelength in the diffraction data
    
    Returns:
        **SinTheta** python list of floating point values with the position of each hkl in 2-theta
        *Is this in radians or degrees? Returning theta or two_theta?*
        
    """
    D=[phase_lattice_parameter/ math.sqrt(hkl[0]*hkl[0]+hkl[1]*hkl[1]+hkl[2]*hkl[2]) for hkl in hkl_list]
    SinTheta=[1*wavelength/(2*d) for d in D]
    return SinTheta

#####################################
def find_two_theta_in_range(sin_theta, hist):
    """
    **Depricated?**
    Truncate the list of possible peak positions (theoretical calculation?) to the range of data.
    Mark values outside this range with np.nan
    
    Args:
        SinTheta: List of peaks in terms of sin(theta)
        hist: GSAS-II histogram
    
    Returns:
        **TwoThetaInRange** python list of peak locations in the two theta range.
    """
    two_theta=[np.nan]*len(sin_theta)
    for i,value in enumerate(sin_theta):
        try:
            two_theta[i]=(2*math.degrees(math.asin(value)))
        except:
            two_theta[i]=(np.nan)

    two_theta_in_range=[np.nan if i > max(hist.data['data'][1][0]) else i for i in two_theta]
    two_theta_in_range=[np.nan if i < min(hist.data['data'][1][0]) else i for i in two_theta_in_range]
    return two_theta_in_range

#####################################
######### Analysis Fuctions #########
#####################################

#####################################
def get_theoretical_intensities(gpx_file_name,material,cif_file, \
        instrument_calibration_file,xtal_data, \
        x_range,G2sc,DataPathWrap,SaveWrap, DF_flags_for_user):
    """
    Function to calculate the theoretical intensities.
    Simulated diffraction profile calculated based on the .cif file and instrument parameter file
    
    Args:
        gpx_file_name: GSAS-II datafile (ends in .gpx)
        material: Short name for the material (phase) for the dataframe e.g., 'Austenite', 'Ferrite'
        cif_file: Crystallographic Information Format file for the phase to be simulated
        instrument_calibration_file: instrument parameter file
        xtal_data: crystal data from json file
        x_range: two_theta range to calculate over (x-axis). List of length 2
        G2sc: GSAS-II scriptable module.  Passed to resolve the pathway
        DataPathWrap: Path prefix to the location of the datafiles to read
        SaveWrap: Path prefix to the location where new data should be saved
    
    Returns:
        **ti_table** Pandas dataframe with theoretical intensities
        
    Raises:
    
    """
    
    # Create a GSAS-II project to save data to
    gpx = G2sc.G2Project(newgpx=SaveWrap(gpx_file_name))

    # Add a phase to the project from a .cif file
    Phase = gpx.add_phase(DataPathWrap(cif_file), phasename=material,fmthint='CIF')

    # Arbitrary scale factor.  Value chosen to provide reasonable signal to noise and comparison to input data.
    histogram_scale=100.

    # add a simulated histogram and link it to the previous phase(s)
    # May need to make the two theta range and number of points variables
    hist1 = gpx.add_simulated_powder_histogram(material + " simulation",
                DataPathWrap(instrument_calibration_file),x_range[0],x_range[1],Npoints=5000,
                phases=gpx.phases(),scale=histogram_scale)
    
    # calculate simulated pattern and save file
    gpx.do_refinements()
    gpx.save()
    
    # Extract some of the columns for the reflection list generated by the simulated histogram
    # The description of the reflection list by column
    # https://gsas-ii.readthedocs.io/en/latest/GSASIIobj.html#powderrefl-table
    ti_table = pd.DataFrame(hist1.data['Reflection Lists'][material]['RefList'][:,(0,1,2,3,5,9,11)],columns=['h','k','l','mul','two_theta','F_calc_sq','I_corr'])
    
    ti_table['R_calc']=ti_table['I_corr']*ti_table['F_calc_sq']
    ti_table[['Phase']] = material
    
    # Add column for texture corrections
    
    # Read in from file if there's a 4th column
    if len(xtal_data[material])==4:
        ti_table['Texture Correction'] =xtal_data[material][3]
    # Else, assume no texture
    else:
        ti_table['Texture Correction'] =1
        DF_flags_for_user=flag_phase_fraction(np.nan,"Theoretical Intensities", \
         "No Texture Correction Applied", "Check normalized intensities" ,\
          DF_flags_for_user)
    # Import json file with values
    
    
    # Remove any peaks that have zero theoretical intensity
    # Ran into this for Example 06
    ti_table= ti_table.loc[(ti_table["R_calc"]>0)]
    
    return ti_table

#####################################
def calculate_phase_fraction(Merged_DataFrame, DF_flags):
    """
    **To Be Depricated?**
    Use conventional mean and standard deviation caculations to determine phase fraction. Also includes rounding for display
    
    Args:
        Merged_DataFrame: Pandas DataFrame with combined theoretical and fit data
        DF_flags: Pandas DataFrame that includes flags to the user
    
    Returns:
        | Two items are returned
        | **phase_dict** python dictionary with phase fraction values
        | **DF_flags** Pandas DataFrame that includes flags to the user
    Raises:
    """
    
    # Extract all phases listed
    phase_list=Merged_DataFrame['Phase'].unique()
    n_phases = len(phase_list)
    
    phase_fraction_DF = pd.DataFrame({
        "Phase":phase_list,
        "Phase_Fraction":[0]*n_phases,
        "Phase_Fraction_StDev":[0]*n_phases,
        "Number_hkls":[0]*n_phases,
        "hkls":[np.nan]*n_phases,
        "Mean_nint":[0]*n_phases,
        "StDev_nint":[0]*n_phases
    })

    fraction_dict = {} # DN: not sure why we need this?

    # first, fill in table
    for ii, phase in enumerate(phase_list):
        #print(phase)
        
        Phase_DF=Merged_DataFrame.loc[Merged_DataFrame['Phase'] == phase][['h','k','l','n_int','Peak_Fit_Success']]
        print(Phase_DF)
        #print(Phase_DF['n_int'].loc[(Phase_DF["Peak_Fit_Success"]==True)].mean())

#        phase_fraction_DF["Mean_nint"].iloc[ii] = Phase_DF['n_int'].mean()
#        phase_fraction_DF["StDev_nint"].iloc[ii] = Phase_DF['n_int'].std()
#        phase_fraction_DF["Number_hkls"].iloc[ii] = len(Phase_DF['n_int'])

        # Changed to avoid returning a copy error
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
#        phase_fraction_DF.loc[ii,"Mean_nint"] = Phase_DF['n_int'].mean()
#        phase_fraction_DF.loc[ii,"StDev_nint"] = Phase_DF['n_int'].std()
#        phase_fraction_DF.loc[ii,"Number_hkls"] = len(Phase_DF['n_int'])

        phase_fraction_DF.loc[ii,"Mean_nint"] =Phase_DF['n_int'].loc[(Phase_DF["Peak_Fit_Success"]==True)].mean()
        phase_fraction_DF.loc[ii,"StDev_nint"] =Phase_DF['n_int'].loc[(Phase_DF["Peak_Fit_Success"]==True)].std()
        phase_fraction_DF.loc[ii,"Number_hkls"] =len(Phase_DF['n_int'].loc[(Phase_DF["Peak_Fit_Success"]==True)])

        #print("Add to fraction_dict")
        fraction_dict[phase]=phase_fraction_DF

        if (phase_fraction_DF.loc[ii,"Number_hkls"] != len(Phase_DF['n_int'])):
            DF_flags=flag_phase_fraction(np.nan,"Phase Fraction", ("Peaks that failed to fit in phase "+phase+" were removed"),
             "Improve signal to noise, request assistance on fitting" , DF_to_append=DF_flags)

    # now, compute phase fraction
    phase_fraction_DF["Phase_Fraction"]=phase_fraction_DF["Mean_nint"]/(phase_fraction_DF["Mean_nint"].sum())
    phase_fraction_DF["Phase_Fraction_StDev"]=phase_fraction_DF["StDev_nint"]/(phase_fraction_DF["Mean_nint"].sum())
    norm_intensity_var=phase_fraction_DF.loc[phase_fraction_DF['Phase'] == phase]["Phase_Fraction_StDev"]



    #Uncertainty_DF=flag_phase_fraction(norm_intensity_var.values[0],
    #                                  "Normalized Intensity Variation", phase, np.nan, DF_to_append=Uncertainty_DF)


    # Extracting only the 'Austenite' values
    #? Maybe pass based upon which phase is of interest
    #? or create one for each phase?
    #? Maybe move rounding to display only?
    phase_fraction_DF = phase_fraction_DF.round(6)

    print("Fraction Dictionary")
    #print(fraction_dict)
    print(phase_fraction_DF)
    
    return phase_fraction_DF, DF_flags


#####################################
def flag_phase_fraction(value, source, flag, suggestion, DF_to_append=None):
    """
    Adds notes and flags to austenite calculation.

    Args:
        value: numeric value (float) of flagged value
        source: short string text explaining the what step in the data is flagged
        flag: longer string text describing the alert to user
        suggestion: string text with suggestions on source or mitigation methods to decrease error
        DF_to_append: pandas DataFrame to append flags and notes

    Returns:
        **DF_flags** Pandas DataFrame that includes flags to the user

    Raises:
    """
    
    print("Issue Flagged")
    flags_dict = {"Value":[],"Source":[],"Flags":[],"Suggestions":[]};

    flags_dict["Value"].append(value)
    flags_dict["Source"].append(source)
    flags_dict["Flags"].append(flag)
    flags_dict["Suggestions"].append(suggestion)
    
    flags_DF=pd.DataFrame(data=flags_dict)
    #print("Before appending")
    # append if other dataframe is included
    if DF_to_append is not None:
        flags_DF=pd.concat((DF_to_append,flags_DF), axis=0, ignore_index=True)
    
    #flags_DF.sort_values(by=["Value"],inplace=True)
    
    return flags_DF

def create_norm_intensity_graph(DF_merged_fit_theo, tis, DF_phase_fraction, two_theta, dataset):
    """
    Creates plot of variation in normalized intensities.  The visualization can offer the user feedback on the sources of variation.

    Args:
        DF_merged_fit_theo: dataframe of fit values(Dataframe)
        tis: Dataframe of theoretical intensities (Dataframe)
        DF_phase_fraction: Dataframe of phase fraction values (Dataframe)
        two_theta: List of two thetas(List)
        
    Returns:
        **fig_norm_intensity** plotly express figure showing the variation in normalized intensity for each phase

    Raises:

    """
    if DF_merged_fit_theo.shape[0] == tis.shape[0]:
        fig_norm_intensity = go.Figure()
        phase_list = DF_merged_fit_theo['Phase'].unique().tolist()
        for i in range(len(phase_list)):
        
            temp_df = DF_merged_fit_theo.loc[DF_merged_fit_theo.Phase == phase_list[i],:]
            uncert_y = np.array(np.sqrt(temp_df['u_pos_fit']**2 + temp_df['u_int_fit']**2 + temp_df['u_cryst_diff']**2)/temp_df['R_calc'])

            for j in range(len(uncert_y)):
                uncert_y[j] = np.min( (uncert_y[j],temp_df['n_int'].iloc[j]*3) )  # to prevent absurd uncertainties from the fitting, eg. mean = 32, uncert = 10^6

            fig_norm_intensity.add_trace(go.Scatter(x=temp_df['pos_fit'],
                                                    y=temp_df['n_int'],
                                                    mode='markers',
                                                    error_y=dict(type='data',array=uncert_y,visible=True),
                                                    name=phase_list[i] + '(' + str(dataset) + ')'))

        # I'd like to have the color be the same, but haven't figured out how.
        for i,value in enumerate(DF_phase_fraction["Mean_nint"]):
            
            fig_norm_intensity.add_trace(
                        go.Scatter(
                            x=two_theta,
                            y=[value]*len(two_theta),
                            mode='lines',
                            line=dict(color='dimgray',width=1),
                            name="Mean "+DF_phase_fraction["Phase"][i] + '(' + str(dataset) + ')')
                        )
            
            upr = value + DF_phase_fraction['StDev_nint'].iloc[i]
            lwr = value - DF_phase_fraction['StDev_nint'].iloc[i]
            fig_norm_intensity.add_trace(
                        go.Scatter(
                            x=two_theta,
                            y=[upr]*len(two_theta),
                            mode='lines',
                            showlegend=False,
                            line=dict(dash='dash',color='dimgray',width=1))
                        )
            
            fig_norm_intensity.add_trace(
                        go.Scatter(
                            x=two_theta,
                            y=[lwr]*len(two_theta),
                            mode='lines',
                            showlegend=False,
                            line=dict(dash='dash',color='dimgray',width=1))
                        )
        
        ## Add crosses to indicate values that didn't work
        fig_norm_intensity.add_trace(
                        go.Scatter(
                            x=DF_merged_fit_theo["pos_fit"].loc[(DF_merged_fit_theo["Peak_Fit_Success"]==False)],
                            y=DF_merged_fit_theo["n_int"].loc[(DF_merged_fit_theo["Peak_Fit_Success"]==False)],
                            mode="markers",
                            name="Excluded from Analysis",
                            marker_symbol='x',
                            marker_color='red',
                            marker_size = 8
                            )
                        )
    else:
        print("Warning: I and R values different lengths. Returning empty figure.")
        print(DF_merged_fit_theo)
        fig_norm_intensity = go.Figure()

    return fig_norm_intensity

def create_fit_fig(two_thetas, intensity_list, dataset):
    """
    Creates plot of fit intensity vs two_theta data

    Args:
        two_thetas: list of two_theta values
        intensity_list: list of various fitted intensity data(raw, fit, background)
        dataset: current dataset graph being created
        
    Returns:
        **fig_fit_hist** plotly figure of fit intensity vs two_theta data

    Raises:

    """
    fig_fit_hist = go.Figure()

    fig_fit_hist.add_trace(go.Scatter(x=two_thetas,y=intensity_list[0],mode='markers',name='data: ' + str(dataset)))
    fig_fit_hist.add_trace(go.Scatter(x=two_thetas,y=intensity_list[1],mode='markers',name='background: ' + str(dataset)))
    fig_fit_hist.add_trace(go.Scatter(x=two_thetas,y=intensity_list[2],mode='lines',name='fit: ' + str(dataset)))

    fig_fit_hist.update_layout(
        title="",
        xaxis_title="2theta",
        yaxis_title="Intensity"
    )

    return fig_fit_hist


def create_instprm_file(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc):
    """
    Create an instrument parameter file if none exists.  Copy of the fitting framework.  Instrument parameter file is available for saving by the user.
    
    Args:
        datadir: Location data is stored
        workdir: Working directory for data
        xrdml_fname: Diffraction data (xrdml title legacy)
        instprm_fname: Instrument Parameter File
        cif_fnames: Crystollographic Info File
        G2sc: GSAS-II Scripting Toolkit location
    
    Returns:
    """
    
    #Helper functions to create full path descriptions
    data_path_wrap = lambda fil: datadir + '/' + fil
    save_wrap = lambda fil: workdir + '/' + fil
    
    # start new GSAS-II project
    gpx = G2sc.G2Project(newgpx=save_wrap('pkfit.gpx'))

    #initialize Uncertainty DataFrame
    DF_flags_for_user=flag_phase_fraction(np.nan, " ", "Initialize", " ")

    #############################
    # Read in diffraction data
    #############################
    print("\n\n Read in diffraction data\n")
    
    # read in diffraction data as a powder histogram
    # Do this first to get the two_theta range
    hist = gpx.add_powder_histogram(data_path_wrap(xrdml_fname),
                                    data_path_wrap(instprm_fname),
                                    databank=1, instbank=1)

    # Get the two_theta range of the histogram
    two_theta_range=hist.getdata('X')
    min_two_theta=min(two_theta_range)
    max_two_theta=max(two_theta_range)
    #print(min_two_theta,max_two_theta)

    ########################################
    # Caculate the theoretical intensities from cif files
    ########################################
    #? Could this be merged with Read in Phase data?
    print("\n\n Calculate Theoretical Intensities\n")

    tis = {} # e.g. tis['austenite-duplex.cif'] maps to austenite theoretical intensities

    for i in range(len(cif_fnames)):
        tis[cif_fnames[i]] = get_theoretical_intensities(gpx_file_name=cif_fnames[i] + '.gpx',
                                                         material=cif_fnames[i],
                                                         cif_file=cif_fnames[i],
                                                         instrument_calibration_file=instprm_fname,
                                                         G2sc=G2sc,
                                                         x_range=[min_two_theta,max_two_theta],
                                                         DataPathWrap=data_path_wrap,
                                                         SaveWrap=save_wrap)

    # Merge and sort the theoretical intensities
    #? Sort seems a kind of fragile way to align the data 
    tis = pd.concat(list(tis.values()),axis=0,ignore_index=True)
    tis = tis.sort_values(by='two_theta')
    tis = tis.reset_index(drop=True)
    print("\n\n Theoretical Intensity Dataframe")
    print(tis)

    ########################################
    # Read in phase data
    ########################################
    print("\n\n Read in Phase Data\n")

    phases = {}
    a0 = {}
    for i in range(len(cif_fnames)):
        phases[cif_fnames[i]] = get_phase(data_path_wrap(cif_fnames[i]), cif_fnames[i], gpx) # phase data
        a0[cif_fnames[i]] = phases[cif_fnames[i]].data['General']['Cell'][1] # lattice parameter

    # Find the ka1 wavelength in the file
    # works for some data files that have information encode, otherwise may need to prompt
    try:
        #Ka1_wavelength=float([s for s in hist.data['Comments'] if s.startswith('Ka1')][0].split('=')[1])
        # pull from instrument parameters not comments
        Ka1_wavelength=hist.data['Instrument Parameters'][0]['Lam1'][0]
    except:
        # hardcoded in for now with Cu source.
        #? Read from instrument parameter file? Prompt user?
        Ka1_wavelength=1.5405
        DF_flags_for_user=flag_phase_fraction(0,"Histogram Data", "Assumed Cu single wavelength", "Check input file", DF_to_append=DF_flags_for_user)

    ########################################
    # use the theoretical intensities for peak fit location
    ########################################
    print("\n\n Peak Fit (LeBail) of Experimental Data \n")

    # use the theoretical intensities for peak fit location
    peaks_list=tis['two_theta']
    
    # Add to the two_theta values to move the peak location for debugging
    # 0.2 on example 5 is enough to throw off the last two peaks
    # 0.5 on example 5 will result in negative intensities being fit
    # tis['two_theta']+= 0.5
    #peaks_list=tis['two_theta']+0.5

    peaks_ok = False
    fit_attempts = 0
    fit_attempt_limit = 3
    peak_verify = []
    t_peaks = 0
    t_sigma = 0
    t_gamma = 0
    t_int = 0
    t_pos = 0

    while not (peaks_ok):
        print("\n\n Fit attempt number ", fit_attempts," \n")
        if(fit_attempts == 0):
            fit.fit_peaks(hist, peaks_list)
        # Currently the fit processes are a little different...
        elif(fit_attempts == 1):
            fit.fit_moved_right_peaks(hist, peaks_list, peak_verify)
            DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Moving initial fit location to a lower 2-theta value", "Adjust lattice spacing in .cif files", DF_to_append=DF_flags_for_user)
        elif(fit_attempts == 2):
            fit.fit_moved_left_peaks(hist, peaks_list, peak_verify)
            DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Moving initial fit location to a higher 2-theta value", "Adjust lattice spacing in .cif files", DF_to_append=DF_flags_for_user)
        elif(fit_attempts == 3):
            holding_sig = False
            holding_gam = True
            for x in range(6):
                if not(np.all(peak_verify == True)):
                    if holding_gam:
                        fit.fit_peaks_holdgam(hist, peaks_list, Chebyschev_coeffiecients, peak_verify)
                        holding_gam = False
                        holding_sig = True
                    elif holding_sig:
                        fit.fit_peaks_holdsig(hist, peaks_list, Chebyschev_coeffiecients, peak_verify)
                        holding_sig = False
                        holding_gam = True
            t_peaks = pd.DataFrame(hist.data['Peak List']['peaks'])
            t_sigma = t_peaks.iloc[:,4]
            t_gamma = t_peaks.iloc[:,6]
            t_int = t_peaks.iloc[:,2]
            t_pos = t_peaks.iloc[:,0]
            peak_verify = fit.create_verify_list(t_pos, t_int, t_sigma, t_gamma)

        t_peaks = pd.DataFrame(hist.data['Peak List']['peaks'])
        t_sigma = t_peaks.iloc[:,4]
        t_gamma = t_peaks.iloc[:,6]
        t_int = t_peaks.iloc[:,2]
        t_pos = t_peaks.iloc[:,0]

        peak_verify = fit.create_verify_list(t_pos, t_int, t_sigma, t_gamma)

        fit_attempts += 1

        if(np.all(peak_verify == True)):
            print("\n\n All values are within a likeable range \n")
            peaks_ok = True
        
        elif(fit_attempts >= fit_attempt_limit):
            print("\n\n Intensities and Positions are NOT all positive, HOWEVER iteration limit reached \n")
            peaks_ok = True
            DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Limit of Fitting attempts reached", "Adjust lattice spacing in .cif files", DF_to_append=DF_flags_for_user)
            
        else:
            print("\n\n Intensities and Positions are NOT all positive, retrying \n")
            peaks_ok = False
            DF_flags_for_user=flag_phase_fraction(np.nan,"Fitting", "Intensities and Positions are NOT all positive, retrying", "Retrying fitting" , DF_to_append=DF_flags_for_user)
            # reset the peak list in the histogram to avoid appending during successive attempts
            hist.data['Peak List']['peaks']=[]
            # reset and repopulate the peak list
            peaks_list=tis['two_theta']

    fit.fit_instprm_file(hist, peaks_list)
    hist.SaveProfile("created_instprm")

def get_conversions(phase_frac,cell_masses,cell_volumes):

    """
    *ADD*
    
    Parameters:
        phase_frac: *ADD*
        cell_masses: *ADD*
        cell_volumes: *ADD*

    
    Returns:
        | *ADD*
        |
        
    Raises:

    
    """
    
    # deepcopy to prevent aliasing
    mass_conversion = deepcopy(phase_frac)
    volume_conversion = deepcopy(phase_frac)
    
    #find denominator first(normalize at the same time)
    n_phases = len(phase_frac["Dataset: 1"][0])

    cell_mass_vec = np.zeros(n_phases)
    cell_volume_vec = np.zeros(n_phases)
    cell_number_vec = np.zeros(n_phases)

    for ii in range(n_phases):
        cell_mass_vec[ii] = cell_masses[phase_frac['Dataset: 1'][0][ii]['Phase']]
        cell_volume_vec[ii] = cell_volumes[phase_frac['Dataset: 1'][0][ii]['Phase']]
        cell_number_vec[ii] = phase_frac['Dataset: 1'][0][ii]['Phase_Fraction']

    for dataset in phase_frac:

        for ii in range(n_phases):
            mass_conversion[dataset][0][ii]['Phase_Fraction'] = cell_number_vec[ii]*cell_mass_vec[ii]/np.sum(cell_number_vec*cell_mass_vec)
            volume_conversion[dataset][0][ii]['Phase_Fraction'] = cell_number_vec[ii]*cell_volume_vec[ii]/np.sum(cell_number_vec*cell_volume_vec)

    return mass_conversion, volume_conversion, cell_mass_vec, cell_volume_vec

def convert_mu_samps(mu_samps,conversion_vec):

    """
    *ADD*
    
    Parameters:
        mu_samps: *ADD*
        conversion_vec: *ADD*

    
    Returns:
        | *ADD*
        |
        
    Raises:

    
    """

    c = conversion_vec
    mu_samps = mu_samps.apply(lambda x: x*c/np.sum(x*c),axis=1,raw=True)

    return mu_samps

def compute_peak_fitting(datadir,workdir,xrdml_fnames,instprm_fname,cif_fnames,crystal_data,G2sc):
    print("Running peak fitting...")
    results_table = {}
    phase_frac = {}
    two_thetas = {}
    uncert = {}
    ti_tables = {}
    altered_results = {}
    altered_phase = {}
    altered_ti = {}
    fit_points = {}
    #create the above dicts to store data returned from compute_results
    for x in range(len(xrdml_fnames)):
        print("Compute results for file ",x)
        fit_data, results_df, phase_frac_DF, two_theta, tis, uncert_DF = compute(datadir,workdir,xrdml_fnames[x], \
                                    instprm_fname,cif_fnames,crystal_data, G2sc)
        temp_string = 'Dataset: ' + str(x + 1)
        results_df['sample_index'] = str(x + 1)
        
        #store data in their respective dictionaries, with the keys being the current dataset(1,2,...) and the value being data
        #some are duplicated because they needed to be converted in multiple ways
        results_table[temp_string] = results_df
        phase_frac[temp_string] = phase_frac_DF
        two_thetas[temp_string] = two_theta.tolist()
        ti_tables[temp_string] = tis
        uncert[temp_string] = uncert_DF
        altered_results[temp_string] = results_df
        altered_phase[temp_string] = phase_frac_DF
        altered_ti[temp_string] = tis
        fit_points[temp_string] = fit_data
        print("Finish results for file ",x)

    # full results table
    full_results_table = pd.concat(results_table,axis=0,ignore_index=True)
    full_results_table = full_results_table.loc[full_results_table['Peak_Fit_Success'],:]
    full_results_table['Uncertainties due to Fitting'] = full_results_table['u_int_fit']/full_results_table['R_calc']
    full_results_table['Uncertainties due to Counts'] = full_results_table['u_int_count']/full_results_table['R_calc']
    full_results_table = full_results_table.loc[:,['sample_index','Phase','Uncertainties due to Counts','Uncertainties due to Fitting']]
    u_int_fit_count_table_data, u_int_fit_count_table_columns = df_to_dict(full_results_table.round(6))
    print("Peak fitting complete")

    return {
        'results_table':results_table,
        'phase_frac':phase_frac,
        'two_thetas':two_thetas, 
        'uncert':uncert, 
        'ti_tables':ti_tables,
        'altered_results':altered_results, 
        'altered_phase':altered_phase, 
        'altered_ti':altered_ti, 
        'fit_points':fit_points, 
        'u_int_fit_count_table_data':u_int_fit_count_table_data,
        'u_int_fit_count_table_columns':u_int_fit_count_table_columns
    }

def compute_interaction_volume(cif_fnames,datadir,instprm_fname):

    print("Begin Interaction Volume")
    scattering_dict = {}
    atomic_masses = {}
    elem_fractions = {}
    cell_volumes = {}
    cell_masses = {}
    for x in range(len(cif_fnames)):
        #print("Compute results for cif file ",x)
        print("Compute results for cif file ",cif_fnames[x])
        cif_path = os.path.join(datadir, cif_fnames[x])
        instprm_path = os.path.join(datadir, instprm_fname)
        
        addon = False
        elems = []
        crystal_density = None
        print("Begin Open files")
        # Somewhat fragile to cif format and number of returns after line ending
        with open(cif_path) as f:
            lines = f.readlines()
            for line in lines:
                if len(line.split()) > 0:
                    if line.split()[0] == '_cell_volume':
                        cell_volumes[cif_fnames[x]] = (float(line.split()[1].split('(')[0]))
                    if line.split()[0] == '_exptl_crystal_density_diffrn':
                        crystal_density = float(line.split()[1])
                if addon == True and len(line) > 1:
                    elems.append(line)
                if addon == True and len(line) <= 1:
                    addon = False
                #changed to string comparison as the syntax changed some
                if 'symmetry_multiplicity' in line:
                    addon = True
        
        print("Begin parameter files readin")
        wavelengths = []
        with open(instprm_path) as fi:
            lines = fi.readlines()
            for line in lines:
                if line != '#GSAS-II instrument parameter file; do not add/delete items!':
                    line_split = line.split(':')
                    if line_split[0] == 'Lam1' or line_split[0] == 'Lam2' or line_split[0] == 'Lam':
                        wavelengths.append(float(line_split[1].strip('\n')))
        
        print("Element Calculation")
        elems_for_phase = []
        elem_percentage = []
        atoms_per_cell = None
        
        # Should throw an error message if the list is blank...
        for elem in elems:
            print("running element ", elem)
            temp = elem.split()
            elems_for_phase.append(temp[1])
            elem_percentage.append(float(temp[5]))
            atoms_per_cell = int(temp[8])
            #print("Results: ", elems_for_phase, elem_percentage,atoms_per_cell)
        
        print("Cell Volume Calculation")
        cell_mass = 0.0
        count = 0
        for elem in elems_for_phase:
            key = elem + '_'
            elem_mass = atmdata.AtmBlens[key]['Mass']
            # included the atoms per cell here
            cell_mass += elem_mass * elem_percentage[count] * atoms_per_cell
            atomic_masses[elem] = elem_mass
            print("Element: ", elem,"\tMass: ",elem_mass)
            count += 1
        
        cell_masses[cif_fnames[x]] = cell_mass
        print(cell_mass, ' ', cell_masses)

        print("Begin Cell Density")
        cell_density = cell_mass/cell_volumes[cif_fnames[x]]
        pack_fraction = crystal_density/cell_density
        #print(cell_density,pack_fraction)
        elem_details = getFormFactors(elems_for_phase)
        #print(elem_details)
        scattering_nums = []
        for elem in elem_details:
            #print(elem)
            scattering_nums.append(findMu(elem, wavelengths, pack_fraction, cell_volumes[cif_fnames[x]])) #scattering nums has elem_sym, f', f'', and mu
            #print(elem, scattering_nums)
        
        print("Begin Cell Scattering")
        for elem in scattering_nums:
            elem[1] = elem[1][0]
            elem[2] = elem[2][0]
            elem.append(atoms_per_cell)

        scattering_dict[cif_fnames[x]] = scattering_nums
        elem_fractions[cif_fnames[x]] = elem_percentage
        
    print("Interaction Volume Computation Complete")

    return {
        'scattering_dict':scattering_dict,
        'atomic_masses':atomic_masses,
        'elem_fractions':elem_fractions,
        'cell_volumes':cell_volumes,
        'cell_masses':cell_masses
    }

def run_mcmc(results_table,fit_vi,number_mcmc_runs):

    results_table_df = pd.concat(results_table,axis=0).reset_index()
    mcmc_df = run_stan(results_table,int(number_mcmc_runs),fit_vi)
    unique_phases = np.unique(results_table_df.Phase)
    param_table = generate_param_table(mcmc_df,unique_phases,results_table_df)

    mcmc_df.drop(inplace=True,columns=mcmc_df.columns[mcmc_df.columns.str.contains('sigma')])
    print("{} mcmc samples obtained.".format(mcmc_df.shape[0]))
    print(mcmc_df.info(memory_usage=True))

    return {'mcmc_df':mcmc_df, 'param_table':param_table}

def compute_crystallites_illuminated(crystal_data,peaks_dict,results_table,phase_frac):
    
    crystallites_dict = {}
    #run calculations for each peak of each phase, crystallites dict has keys for phases and values are [[]] with each inner list as a peak in that phase
    
    # add a try/except here to confirm the filenames match
    
    print("Peaks dictionary")
    print(peaks_dict)
    
    crystallites_uncertainties = {}

    # initialize crystiallites diffracted counts to 0
    for dname in results_table.keys():
        results_table[dname]['u_cryst_diff'] = 0

    # Same dataset ok since the material is nominally the same?
    for cif_name, peak_data in peaks_dict.items():
        print("Phase: ", cif_name)
        for x in range(len(peak_data)):
            
            # this calculation is redundant, so we can potentially move outside the loop, but overhead is minimal in the meantime
            crystal_data = format_crystal_data(crystal_data,cif_name) # <- adam may fix the formatting on the json files to make this not necessary

            num_layer, num_ill, frac_difrac, num_difrac = crystallites_illuminated_calc(crystal_data,
                phase_frac['Dataset: 1'].loc[phase_frac['Dataset: 1']['Phase'] == cif_name, 'Phase_Fraction'].values[0],
                crystal_data[cif_name][0],
                crystal_data[cif_name][1],
                peak_data[x][1],
                peak_data[x][2],
                crystal_data[cif_name][2])
            if cif_name in crystallites_dict.keys():
                crystallites_dict[cif_name].append([num_layer, num_ill, frac_difrac, num_difrac])
            else:
                crystallites_dict[cif_name] = []
                crystallites_dict[cif_name].append([num_layer, num_ill, frac_difrac, num_difrac])
            
            # add in uncertainties due to number crystallites diffracted
            cd_uncert = np.sqrt(crystallites_dict[cif_name][x][3]) # uncertainty value
            row_bool = (results_table['Dataset: 1'].Phase == cif_name) & (np.abs(results_table['Dataset: 1']['pos_fit'] - peak_data[x][2]*2) < .01) # find correct row using cif name and peak_data[x][2], which is pos_fit/2
            results_table['Dataset: 1'].u_cryst_diff.loc[row_bool] = cd_uncert

    return {'crystallites_dict':crystallites_dict, 
            'results_table':results_table}

def format_crystal_data(crystal_data,cif_name):
    """
    Reformats the crystal data objects from json to expected types.
    
    Args:
        crystal_data: crystal_data object loaded from json file
        cif_name: the cif name
    
    Returns:
        **crystal_data** correctly formatted crystal_data object

    """

    # convert eg, '[1,2,3]' to [1,2,3]
    if type(crystal_data[cif_name]) is not list:
        crystal_data[cif_name] = crystal_data[cif_name][1:(len(crystal_data[cif_name])-1)].split(",")
        crystal_data[cif_name] = [float(x) for x in crystal_data[cif_name]]

    for name in ['beam_size','raster_x','raster_y','L','W_F','H_F','H_R']:

        if name in crystal_data.keys():
            crystal_data[name] = float(crystal_data[name])

    return crystal_data

def compute_peaks_dict(cif_fnames,results_table,scattering_dict,elem_fractions):
    peaks_dict = {}
    for phase_name in cif_fnames:
        peaks_dict[phase_name] = []
        
    # Peak dictionary includes F value, multiplicity, theta position, F_squared value
    # doesn't seem like the values are quite right... AC 3 Mar 2023
    for row in results_table['Dataset: 1'].iterrows():
        current_peak = []
        current_peak.append(math.sqrt(row[1]['F_calc_sq'])/scattering_dict[row[1]['Phase']][0][4])
        current_peak.append(row[1]['mul'])
        current_peak.append(row[1]['pos_fit']/2)
        final_FF = 0.0
        for elem in scattering_dict[row[1]['Phase']]:
            count = 0
            FF=(elem[4]*(current_peak[0]+elem[1]))**2+(elem[4]*elem[2])**2
            final_FF += FF * elem_fractions[row[1]['Phase']][count]
            count += 1
        current_peak.append(final_FF)
        peaks_dict[row[1]['Phase']].append(current_peak)
    
    return peaks_dict

def compute_summarized_phase_info(scattering_dict,elem_fractions,peaks_dict):
    summarized_phase_info = {}
    for key, value in scattering_dict.items():
        summarized_phase_info[key] = [0.0,0.0, 0.0]
        current_fracs = elem_fractions[key]
        for i in range(len(value)):
            summarized_phase_info[key][0] += (value[i][1] * current_fracs[i])
            summarized_phase_info[key][1] += (value[i][2] * current_fracs[i])
            summarized_phase_info[key][2] += (value[i][3] * current_fracs[i])
    
    graph_data_dict = {}
    for key, value in peaks_dict.items():
        current_summarized_data = summarized_phase_info[key]
        graph_data_dict[key] = []
        for peak in value:
            data_list = create_graph_data(peak, current_summarized_data)
            graph_data_dict[key].append(data_list)
        #create a dict with keys as phases, nested list with each inner list being that peaks f_elem, mul, and theta

    return graph_data_dict

def gather_example(example_name):

    if example_name == 'Example01':
        datadir = '../ExampleData/Example01'
        cif_fnames = ['austenite-Duplex.cif','ferrite-Duplex.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper_power.xrdml']
        instprm_fname = 'TestCalibration.instprm'
        json_fname = 'Example01.json'

    elif example_name == 'Example05':
        datadir = '../ExampleData/Example05'
        cif_fnames = ['austenite-SRM487.cif','ferrite-SRM487.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['E211110-AAC-001_019-000_exported.csv']
        instprm_fname = 'BrukerD8_E211110.instprm'
        json_fname = 'Example05.json'

    elif example_name == "Example06":
        datadir = '../ExampleData/Example06'
        cif_fnames = ['alpha-prime-martensite-SRI.cif','epsilon-martensite-SRI.cif','austenite-SRI.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['Example06_simulation_generation_data.csv']
        instprm_fname = 'BrukerD8_E211110.instprm'
        json_fname = 'Example06.json'

    elif example_name == "Example08A":
        datadir = '../ExampleData/Example08A'
        cif_fnames = ['austenite-FeOnly.cif','ferrite-FeOnly.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['QP980_AR_th-tthscan_AR0p5_trunc.csv']
        instprm_fname = 'ThomasXRD-Co-Cal.instprm'
        json_fname = 'QP_A.json'

    return datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname

def process_uploaded_data(xrdml_contents,
                          xrdml_fnames,
                          instprm_contents,
                          instprm_fname,
                          cif_contents,
                          cif_fnames,
                          csv_contents,
                          json_fname):
    
    datadir = '../server_datadir'
    workdir = '../server_workdir'

    # For each uploaded file, save (on the server)
    # ensuring that the format matches what GSAS expects.

    # first, read instrument parameter file

    instprm_type, instprm_string = instprm_contents.split(',')

    decoded = base64.b64decode(instprm_string)
    f = open(datadir + '/' + instprm_fname,'w')
    to_write = decoded.decode('utf-8')
    if re.search('(instprm$)',instprm_fname) is not None:
        to_write = re.sub('\\r','',to_write)
    f.write(to_write)
    f.close()


    ####FIX
    # Is this for the export data as csv, or illuminated json file?
    # AC 7 June 2023 - I think this is for the json file but what?
    csv_type, csv_string = csv_contents.split(',')

    decoded = base64.b64decode(csv_string)
    f = open(datadir + '/' + json_fname,'w')
    to_write = decoded.decode('utf-8')
    csv_string = to_write
    if re.search('(csv$)',json_fname) is not None:
        to_write = re.sub('\\r','',to_write)
    f.write(to_write)
    f.close()
    
    # next, read the cif files
    for i in range(len(cif_contents)):
        contents = cif_contents[i]
        fname = cif_fnames[i]
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        f = open(datadir + '/' + fname,'w')
        to_write = decoded.decode('utf-8')
        to_write = re.sub('\\r','',to_write)
        f.write(to_write)
        f.close()
    
    for i in range(len(xrdml_contents)):
        contents = xrdml_contents[i]
        fname = xrdml_fnames[i]
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        f = open(datadir + '/' + fname,'w')
        to_write = decoded.decode('utf-8')
        to_write = re.sub('\\r','',to_write)
        f.write(to_write)
        f.close()

    return datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname

def process_data_input(use_default_files,
                       use_example05_files,
                       use_example06_files,
                       use_example08A_files,
                       xrdml_contents,
                       xrdml_fnames,
                       instprm_contents,
                       instprm_fname,
                       cif_contents,
                       cif_fnames,
                       csv_contents,
                       json_fname):

     ### Gather inputs, either one of the example files, or user upload
    
    if use_default_files not in [None, []] and use_default_files[0] == 1:
        using_example_file = True
        example_name = "Example01"
    # Use Example05 data
    #? Need to fix the austenite cif file names.  compute_results assumes a name.  Should use uploaded names?
    #? Maybe pass like the xrdml_fnames?
    elif use_example05_files not in [None, []] and use_example05_files[0] == 1:
        using_example_file = True
        example_name = "Example05"
        
    elif use_example06_files not in [None, []] and use_example06_files[0] == 1:
        using_example_file = True
        example_name = "Example06"

    elif use_example08A_files not in [None, []] and use_example08A_files[0] == 1:
        using_example_file = True
        example_name = "Example08A"

    # User uploaded data
    else:
        using_example_file = False

    if using_example_file:
        datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname = gather_example(example_name)
    else:
        datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname = process_uploaded_data(xrdml_contents,
                                                                                                      xrdml_fnames,
                                                                                                      instprm_contents,
                                                                                                      instprm_fname,
                                                                                                      cif_contents,
                                                                                                      cif_fnames,
                                                                                                      csv_contents,
                                                                                                      json_fname)

    ### Read in JSON File
    # Needed earlier for some of the theoretical intensity data
    # AC 2023 June 07 - why here?
        #crystal_data = json.loads(json_string)
    
    #need to convert strings to numbers in json dict
    
    # May need to adjust for multi array
    #AC - Why use strings? Try without
#        for key in crystal_data.keys():
#            if(key != 'beam_shape'):
#                if(crystal_data[key][0] == '['):
#                    crystal_data[key] = crystal_data[key].strip('][').split(',')
#                    for x in range(len(crystal_data[key])):
#                        crystal_data[key][x] = float(crystal_data[key][x])
#                else:
#                    crystal_data[key] = float(crystal_data[key])
    
    with open(os.path.join(datadir, json_fname), 'r') as f:
        crystal_data = json.loads(f.read())

    return datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, crystal_data
