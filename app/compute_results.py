from tkinter import TRUE
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
import fit
import compute_uncertainties

def compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc):
    """

    Main computation program for phase calculations
    
    Args:
        datadir: Location data is stored
        workdir: Working directory for data
        xrdml_fname: Diffraction data (xrdml title legacy)
        instprm_fname: Instrument Parameter File
        cif_fnames: Crystollographic Info File
        G2sc: GSAS-II Scripting Toolkit location
    
    Returns:
        fig_raw_hist: Intensity vs. two_theta plot of raw data
        fig_fit_hist: Intensity vs. two_theta plot with fit data
        DF_merged_fit_theo: pandas DataFrame with collected fit and theoretical intensities
        fig_norm_itensity: Figure of normalized intensities
        fig_raw_fit_compare_two_theta: two_theta plot of raw data vs. two_theta plot with fit data
        DF_phase_fraction: pandas DataFrame with phase fraction
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
    
    #breakpoint()

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

    #print(hist.data['Peak List']['peaks'])
    #print(hist.data['Peak List']['sigDict'])
    #hist.Peaks['sigDict'][name]

    # Extract information from the peak fits.
    #? Similarly, sort here seems like a fragile way to align the data.
    DF_merged_fit_theo = pd.DataFrame(hist.data['Peak List']['peaks'])
    DF_merged_fit_theo = DF_merged_fit_theo.iloc[:,[0,2,4,6]]
    DF_merged_fit_theo.columns = ['pos_fit','int_fit','sig_fit','gam_fit']
    
    DF_merged_fit_theo["Peak_Fit_Success"]= peak_verify
    DF_merged_fit_theo["Peak_Fit_Success"] = DF_merged_fit_theo["Peak_Fit_Success"].astype('bool')
    
    #print(DF_merged_fit_theo)
    
    #print(list(range(len(DF_merged_fit_theo.index))))
    #print(hist.data['Peak List']['sigDict']['int0'])
    
    ##### Extract uncertainties from the fitting process
    u_pos_fit_list=[]
    u_int_fit_list=[]
    for i in list(range(len(DF_merged_fit_theo.index))):
        #print(i)
        u_pos_fit_list.append(hist.data['Peak List']['sigDict']['pos'+str(i)])
        u_int_fit_list.append(hist.data['Peak List']['sigDict']['int'+str(i)])
        #print(hist.data['Peak List']['sigDict']['int'+str(i)])
        #print(hist.data['Peak List']['sigDict']['pos'+str(i)])

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
    #print(DF_merged_fit_theo)

    #DF_merged_fit_theo = DF_merged_fit_theo.loc[(0 < DF_merged_fit_theo.sig) & (DF_merged_fit_theo.sig < 90),:]
    #print(DF_merged_fit_theo)

    # Merge the theoretical and experimental peak values
    # Uses the sorting for alignment of rows.  Likely a better way and/or error checking needed
    #? Should the if/else be a try/except block?
    print("\n\n Concatenating Dataframes\n")
    DF_merged_fit_theo = pd.concat((DF_merged_fit_theo,tis),axis=1)
    DF_merged_fit_theo = DF_merged_fit_theo
    DF_merged_fit_theo['n_int'] = (DF_merged_fit_theo['int_fit']/DF_merged_fit_theo['R_calc'])

    DF_merged_fit_theo['pos_diff'] = DF_merged_fit_theo['pos_fit']-DF_merged_fit_theo['two_theta']


        
    ########################################
    # Calculate the phase fraction
    ########################################
    print("\n\n Calculating Phase Fraction\n")
    DF_phase_fraction, pf_uncertainties, DF_flags_for_user = calculate_phase_fraction(DF_merged_fit_theo, DF_merged_fit_theo, DF_flags_for_user)
    
    ########################################
    ########################################
    # Create Plots
    ########################################
    ########################################
    # Moved all plotting functions to the end, allows use of all data in plot


    ########################################
    # Create Figure of raw data
    ########################################
    # display the raw intensity vs. two_theta data
    print("Create Raw Data Figure \n")
    fig_raw_hist = get_figures(hist)

    ########################################
    # Create Fit Figure
    ########################################
    print("Create Fit Figure \n")

    # Create a figure with the fit data
    #? Does this belong in a function?
    fig_fit_hist = go.Figure()

    fig_fit_hist.add_trace(go.Scatter(x=two_theta,y=h_data,mode='markers',name='data'))
    fig_fit_hist.add_trace(go.Scatter(x=two_theta,y=h_background,mode='markers',name='background'))
    fig_fit_hist.add_trace(go.Scatter(x=two_theta,y=h_fit,mode='lines',name='fit'))

    fig_fit_hist.update_layout(
        title="",
        xaxis_title="2theta",
        yaxis_title="Intensity"
    )

    ########################################
    # Create Plot the Normalized Intensities
    ########################################
    print("Create Normalized Intensities Figure \n")

    if DF_merged_fit_theo.shape[0] == tis.shape[0]:

        fig_norm_itensity = px.scatter(DF_merged_fit_theo, x="pos_fit", y="n_int", color="Phase",
                            labels = {
                                'pos_fit':'2-theta',
                                'n_int':'Normalized Intensity'
                                }
                            )
        # I'd like to have the color be the same, but haven't figured out how.
        for i,value in enumerate(DF_phase_fraction["Mean_nint"]):
            fig_norm_itensity.add_trace(
                        go.Scatter(
                            x=two_theta,
                            y=[value]*len(two_theta),
                            mode='lines',
                            name="Mean "+DF_phase_fraction["Phase"][i] )
                        )
        
        ## Add crosses to indicate values that didn't work
        fig_norm_itensity.add_trace(
                        go.Scatter(
                            x=DF_merged_fit_theo["pos_fit"].loc[(DF_merged_fit_theo["Peak_Fit_Success"]==False)],
                            y=DF_merged_fit_theo["n_int"].loc[(DF_merged_fit_theo["Peak_Fit_Success"]==False)],
                            mode="markers",
                            name="Excluded from Analysis",
                            marker_symbol='x'
                            #fillcolor='#000000',
                            )
                        )
        
        
    else:
        print("Warning: I and R values different lengths. Returning empty figure.")
        print(DF_merged_fit_theo)
        fig_norm_itensity = go.Figure()


    ########################################
    # Create Plot comparing the two theta positions
    ########################################
    print("Create Two Theta Comparison Figure \n")
    
    fig_raw_fit_compare_two_theta = two_theta_compare_figure(DF_merged_fit_theo)

    ########################################
    # Resort dataframes for output
    ########################################
    #DF_phase_fraction = DF_phase_fraction.reindex(columns=["Phase","Phase_Fraction","Phase_Fraction_StDev",
    #        "Number_hkls","hkls","Mean_nint","StDev_nint"])

    return fig_raw_hist, fig_fit_hist, DF_merged_fit_theo, fig_norm_itensity, fig_raw_fit_compare_two_theta, DF_phase_fraction, DF_flags_for_user

#####################################
######### Plotting Fuctions #########
#####################################

#####################################
def df_to_dict(df):
    """
    
    function for converting pandas dataframe to dictionary for dash data_table

    Args:
        df: pandas Dataframe

    Returns:

    """
    out_dict = df.to_dict('records')
    out_columns = [{"name": i, "id": i} for i in df.columns]

    return out_dict, out_columns

#####################################
def get_figures(hist):
    """
    plot the intensity vs. two_theta data of a diffraction profile
    
    Args:
        hist: powder histogram
    
    Returns:
        fig: Figure
        #? what format?
    """
    df = pd.DataFrame({
        "two_theta":hist.data['data'][1][0],
        "intensity":hist.data['data'][1][1]
    })

    # I'd like the lines to be in black, with markers, but I keep failing at that.
    #fig = px.line(x=df['two_theta'],y=df['intensity'],color='#000000')#,markers=True)
    #fig.set_color('black')

    fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')
    return fig

#####################################
def two_theta_compare_figure(Merged_DataFrame):
    """
    plot the difference between fitted vs. theoretical two_theta data
    Should be near zero
    
    Args:
        Merged_DataFrame: Dataframe after merging with fitted and theoretical intensities
    
    Returns:
        fig: Plotly Express Figure
    """
    
    fig = px.scatter(Merged_DataFrame, x="two_theta", y="pos_diff", color="Phase",
                    labels = {
                        'pos_fit':'Diffference between fit and theoretical 2-theta',
                        'two_theta':'two theta value'
                        }
                    )
                    
     ## Add a diagonal line in the background, https://github.com/plotly/plotly_express/issues/143
#    fig = px.line(x=[Merged_DataFrame["two_theta"][0],Merged_DataFrame["two_theta"][-1]],
#                  y=[Merged_DataFrame["two_theta"][0],Merged_DataFrame["two_theta"][-1]])
    
    return fig

#####################################
########## Helper Fuctions ##########
#####################################

#####################################
def get_phase(cif_wrap, phase_name, project):
    """
    Retreieve the phase information from file.  Assumes phase information is stored in a .cif file with format hint (fmthint)
    
    Args:
        cif_wrap: path to file
        phase_name: Name for the phase
        project: GSAS-II project file to add phase to
    
    Returns:
        GSAS-II project file with phase data wrapped in
    """
    return project.add_phase(cif_wrap, phase_name, fmthint = 'CIF')

#####################################
def find_sin_thetas(phase_lattice_parameter, hkl_list, wavelength):
    """

    Calculate the position in two theta for a list of hkls.  Used to mark locations for fitting
    !!! Have only tested cubic crystal symmetry
    
    Args:
        phase_lattice_parameter: lattice parameter
        hkl_list: list of lattice planes (hkl)
        wavelength: dominant wavelength in the diffraction data
    
    Returns:
        List of floating point values with the position of each hkl in 2-theta
        #? Is this in radians or degrees?
        #? Returning theta or two_theta?
        
    """
    D=[phase_lattice_parameter/ math.sqrt(hkl[0]*hkl[0]+hkl[1]*hkl[1]+hkl[2]*hkl[2]) for hkl in hkl_list]
    SinTheta=[1*wavelength/(2*d) for d in D]
    return SinTheta

#####################################
def find_two_theta_in_range(sin_theta, hist):
    """
    #Description
    #? Truncate the calculated 2Theta range?
    Create a list of 2Theta values from the dspacing and wavelength. Mark any non-physical values with np.nan
    
    #Input
    SinTheta:
    hist:
    
    #Returns
    TwoThetaInRange:
    """
    two_theta=[np.nan]*len(sin_theta)
    for i,value in enumerate(sin_theta):
        #print(value)
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
def get_theoretical_intensities(gpx_file_name,material,cif_file,instrument_calibration_file,x_range,G2sc,DataPathWrap,SaveWrap):
    """Function to calculate the theoretical intensities.
    
    Simulated diffraction profile calculated based on the .cif file and instrument parameter file
    
    Args:
        gpx_file_name: GSAS-II datafile (ends in .gpx)
        material: Short name for the material (phase) for the dataframe e.g., 'Austenite', 'Ferrite'
        cif_file: Crystallographic Information Format file for the phase to be simulated
        instrument_calibration_file: instrument parameter file
        x_range: two_theta range to calculate over (x-axis). List of length 2
        G2sc: GSAS-II scriptable module.  Passed to resolve the pathway
        DataPathWrap: Path prefix to the location of the datafiles to read
        SaveWrap: Path prefix to the location where new data should be saved
    
    Returns:
        ti_table: Pandas dataframe with theoretical intensities
        
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
    ti_table = pd.DataFrame(hist1.data['Reflection Lists'][material]['RefList'][:,(0,1,2,5,9,11)],columns=['h','k','l','two_theta','F_calc_sq','I_corr'])
    
    ti_table['R_calc']=ti_table['I_corr']*ti_table['F_calc_sq']
    ti_table[['Phase']] = material
    
    # Remove any peaks that have zero theoretical intensity
    # Ran into this for Example 06
    ti_table= ti_table.loc[(ti_table["R_calc"]>0)]
    
    #print(ti_table)
    return ti_table

#####################################
def calculate_phase_fraction(Merged_DataFrame, DF_merged_fit_theo, DF_flags):
    """Calculate Phase Fraction
    
    Args:
        Merged_DataFrame: combined theoretical and fit DataFrame
        Uncertainty_DF: prior uncertainty DataFrame
    
    Returns:
        phase_dict: dictionary with phase values
    
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
    
    #print(phase_list)

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

    # compute phase fraction uncertainties
    pf_uncertainties = compute_uncertainties.compute_uncertainties(
        I=np.array(DF_merged_fit_theo['int_fit']),
        R=np.array(DF_merged_fit_theo['R_calc']),
        I_unc=np.array(DF_merged_fit_theo['u_int_fit']),
        R_unc=np.zeros(DF_merged_fit_theo.shape[0]),
        nsim=1000,
        phases=DF_merged_fit_theo['Phase']
    )

    #Uncertainty_DF=flag_phase_fraction(norm_intensity_var.values[0],
    #                                  "Normalized Intensity Variation", phase, np.nan, DF_to_append=Uncertainty_DF)


    # Extracting only the 'Austenite' values
    #? Maybe pass based upon which phase is of interest
    #? or create one for each phase?
    #? Maybe move rounding to display only?
    phase_fraction_DF = phase_fraction_DF.round(4)

    print("Fraction Dictionary")
    #print(fraction_dict)
    print(phase_fraction_DF)
    
    return phase_fraction_DF, pf_uncertainties,DF_flags
        #['h','k','l','n_int']
    #df.loc[df['column_name'] == some_value]


#####################################
def flag_phase_fraction(value, source, flag, suggestion, DF_to_append=None):
    """Adds notes and flags to phase fraction.

    calculation to flag phase_fraction

    Args:
        value: uncertainty value (float)
        source: source of uncertainty (string)
        flag: alert to user (string)
        suggestion: suggestions on source or mitigation methods to decrease error (string)
        DF_to_append: pandas DataFrame with notes from other sources

    Returns:
        uncertainty_DF: pandas DataFrame with notes about the phase_fraction calculated
        
        variable: description
        
        examples
        
        caveats

    Raises:
        error: error text
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
        flags_DF=DF_to_append.append(flags_DF, ignore_index=True)
    
    #flags_DF.sort_values(by=["Value"],inplace=True)
    
    #print(DF_to_append)
    #print(flags_DF)
    return flags_DF
