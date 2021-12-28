import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

def compute(datadir,workdir,xrdml_fname,instprm_fname,G2sc):
    """
    #Description
    Main computation program for phase calculations
    
    #Input
    datadir: Location data is stored
    workdir: Working directory for data
    xrdml_fname: Diffraction data (xrdml title legacy)
    instprm_fname: Instrument Parameter File
    G2sc: GSAS-II Scripting Toolkit location
    
    #Returns
    fig1: Intensity vs. two_theta plot of raw data
    fig2: Intensity vs. two_theta plot with fit data
    intensity_table: Collected normalized and theoretical intensities
    tbl_columns: Column names from the intensity table
    ni_fig: Figure of normalized intensities
    """
    
    #Helper functions to create full path descriptions
    data_path_wrap = lambda fil: datadir + '/' + fil
    save_wrap = lambda fil: workdir + '/' + fil
    
    # start new GSAS-II project
    gpx = G2sc.G2Project(newgpx=save_wrap('pkfit.gpx'))

    #Commented out format hint so that other examples work
#    hist = gpx.add_powder_histogram(DataPathWrap(xrdml_fname),
#                                    DataPathWrap(instprm_fname),
#                                    fmthint='Panalytical xrdml (xml)', databank=1, instbank=1)

    # read in diffraction data as a powder histogram
    hist = gpx.add_powder_histogram(data_path_wrap(xrdml_fname),
                                    data_path_wrap(instprm_fname),
                                    databank=1, instbank=1)

    # display the raw intensity vs. two_theta data
    fig1 = get_figures(hist)

    # Read in phase data
    #? Change these to be passed as part of the function?
    #? How to handle more than two phases?
    phase_austenite = get_phase(data_path_wrap("austenite-Duplex.cif"), "Austenite", gpx)
    phase_ferrite = get_phase(data_path_wrap("ferrite-Duplex.cif"), "Ferrite", gpx)

    # Read the lattice parameter 
    a0_Austenite=phase_austenite.data['General']['Cell'][1]
    a0_Ferrite=phase_ferrite.data['General']['Cell'][1]

    # Find the ka1 wavelength in the file
    # works for some data files that have information encode, otherwise may need to prompt
    try:
        Ka1_wavelength=float([s for s in hist.data['Comments'] if s.startswith('Ka1')][0].split('=')[1])
    except:
        # hardcoded in for now with Cu source.
        #? Read from instrument parameter file? Prompt user?
        Ka1_wavelength=1.5405

    
    #hardcoding HKL lists
    #? for now, likely better ways to do this later...
    HKL_BCC=[[1,1,0],[2,0,0],[2,1,1],[2,2,0],[3,1,0],[2,2,2],[3,2,1],[4,1,1]]
    HKL_FCC=[[1,1,1],[2,0,0],[2,2,0],[3,1,1],[2,2,2],[4,0,0],[3,3,1],[4,2,0],[4,2,2]]
    
    # Convert the hkl planes to a sin
    sin_theta_BCC = find_sin_thetas(a0_Ferrite, HKL_BCC, Ka1_wavelength)
    sin_theta_FCC = find_sin_thetas(a0_Austenite, HKL_FCC, Ka1_wavelength)

    # identify make sure all peaks are in range
    two_theta_in_range_BCC=find_two_theta_in_range(sin_theta_BCC,hist)         
    two_theta_in_range_FCC=find_two_theta_in_range(sin_theta_FCC,hist)

    # Create and mark a series of two_theta values to fit diffraction data
    #? Maybe marking the data belongs in a function?
    peaks_list=[]
    peaks_list = np.array(two_theta_in_range_BCC)[~np.isnan(np.array(two_theta_in_range_BCC))]
    peaks_list = np.concatenate((peaks_list,
                            np.array(two_theta_in_range_FCC)[~np.isnan(np.array(two_theta_in_range_FCC))]),
                            axis=0)
    peaks_list=list(peaks_list)

    #? The '0.5' addition is just a hack to get the fits to behave for the default files.
    #? We should find a better way to do this
    # Commented out to check Example05
    #peaks_list=[x+0.5 for x in peaks_list]

    # reset the peak list in case of errors...
    #? Do we need this?  Legacy from jupyter notebook when one could run things
    hist.Peaks['peaks']=[]

    # Set up background refinement
    #? Also maybe belongs in a function
    #? How to adjust the number of background parameters (currently 5)
    hist.set_refinements({'Background': {"no. coeffs": 5,'type': 'chebyschev-1', 'refine': True}})
    hist.refine_peaks()

    two_theta = hist.data['data'][1][0]
    h_data = hist.data['data'][1][1]
    h_background = hist.data['data'][1][4]
    h_fit = hist.data['data'][1][3]

    # Fit all of the peaks in the peak list
    for peak in peaks_list:
        hist.add_peak(1, ttheta=peak)

    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    
    # First fit only the area
    hist.set_peakFlags(area=True)
    hist.refine_peaks()
            
    # Second, fit the area and position
    hist.set_peakFlags(pos=True,area=True)
    hist.refine_peaks()

    # Third, fit the area, position, and gaussian componenet of the width
    hist.set_peakFlags(pos=True,area=True,sig=True)
    hist.refine_peaks()

    #? Also fit the lortenzian (gam) component?
    #? There's a way to keep the fit sig values, instead of having them reset to the instrument parameter

    # Create a figure with the fit data
    #? Does this belong in a function?
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(x=two_theta,y=h_data,mode='markers',name='data'))
    fig2.add_trace(go.Scatter(x=two_theta,y=h_background,mode='markers',name='background'))
    fig2.add_trace(go.Scatter(x=two_theta,y=h_fit,mode='lines',name='fit'))

    fig2.update_layout(
        title="",
        xaxis_title="2theta",
        yaxis_title="Intensity"
    )

    # Caculate the theoretical intensities
    #? Move to function?  That way we also can allow more than 2 phases?
    austenite_tis = get_theoretical_intensities(gpx_file_name='Austenite-sim.gpx',
                                                material='Austenite',
                                                cif_file='austenite-Duplex.cif',
                                                instrument_calibration_file=instprm_fname,
                                                G2sc=G2sc,
                                                DataPathWrap=data_path_wrap,
                                                SaveWrap=save_wrap)

    ferrite_tis = get_theoretical_intensities(gpx_file_name='Ferrite-sim.gpx',
                                              material='Ferrite',
                                              cif_file='ferrite-Duplex.cif',
                                              instrument_calibration_file=instprm_fname,
                                              G2sc=G2sc,
                                              DataPathWrap=data_path_wrap,
                                              SaveWrap=save_wrap)



    #breakpoint()

    # Merge and sort the theoretical intensities
    #? Sort seems a kind of fragile way to align the data
    tis = pd.concat((austenite_tis,ferrite_tis),axis=0,ignore_index=True)
    tis = tis.sort_values(by='two_theta')
    tis = tis.reset_index(drop=True)
    print(tis)
  
    # Extract information from the peak fits.
    #? Similarly, sort here seems like a fragile way to align the data.
    mydf = pd.DataFrame(hist.data['Peak List']['peaks'])
    mydf = mydf.iloc[:,[0,2,4,6]]
    mydf.columns = ['pos','int','sig','gam']
    mydf = mydf.sort_values('pos')
    mydf = mydf.reset_index(drop=True)
    #mydf = mydf.loc[(0 < mydf.sig) & (mydf.sig < 90),:]
    print(mydf)
    #breakpoint()

    # Merge the theoretical and experimental peak values
    # Uses the sorting for alignment of rows.  Likely a better way and/or error checking needed
    #? Should the if/else be a try/except block?
    print("Concatenating Datafiles")
    mydf = pd.concat((mydf,tis),axis=1)
    mydf['n_int'] = mydf['int']/mydf['R_calc']

    if mydf.shape[0] == tis.shape[0]:

        ni_fig = px.scatter(mydf, x="pos", y="n_int", color="Phase",
                            labels = {
                                'pos':'2-theta',
                                'n_int':'Normalized Intensity'
                                }
                            )
    
    else:
        print("Warning: I and R values different lengths. Returning empty figure.")
        print(mydf)
        ni_fig = go.Figure()
    
    # Create a dictionary table for results
    intensity_table = mydf.to_dict('records')
    tbl_columns = [{"name": i, "id": i} for i in mydf.columns]

    # Calculate the phase fraction
    (Phase_Fraction_dict, Phase_Fraction_columns) =Phase_Fraction(mydf)
    
    # create a plot for the two theta
    
    two_theta_fig = two_theta_compare_figure(mydf)

    return fig1, fig2, intensity_table, tbl_columns, ni_fig, two_theta_fig, Phase_Fraction_dict, Phase_Fraction_columns

#####################################
######### Plotting Fuctions #########
#####################################

def get_figures(hist):
    """
    #Description
    plot the intensity vs. two_theta data of a diffraction profile
    
    #Input
    hist: powder histogram
    
    #Returns
    fig: Figure
    #? what format?
    """
    df = pd.DataFrame({
        "two_theta":hist.data['data'][1][0],
        "intensity":hist.data['data'][1][1]
    })

    fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')
    return fig

def two_theta_compare_figure(Merged_DataFrame):
    """
    #Description
    plot the fitted vs. theoretical two_theta data
    Should be along the diagonal
    
    #Input
    Merged_DataFrame: Dataframe after merging with fitted and theoretical intensities
    
    #Returns
    fig: Figure
    #? what format?
    """
    
    fig = px.scatter(Merged_DataFrame, x="two_theta", y="pos", color="Phase",
                    labels = {
                        'pos':'Fitted 2-theta',
                        'two_theta':'Normalized Intensity'
                        }
                    )
                    
     ## Add a diagonal line in the background, https://github.com/plotly/plotly_express/issues/143
#    fig = px.line(x=[Merged_DataFrame["two_theta"][0],Merged_DataFrame["two_theta"][-1]],
#                  y=[Merged_DataFrame["two_theta"][0],Merged_DataFrame["two_theta"][-1]])
    
    return fig

#####################################
########## Helper Fuctions ##########
#####################################

def get_phase(cif_wrap, phase_name, project):
    """
    #Description
    Retreieve the phase information from file.  Assumes phase information is stored in a .cif file with format hint (fmthint)
    
    #Input
    cif_wrap: path to file
    phase_name: Name for the phase
    project: GSAS-II project file to add phase to
    
    #Returns
    GSAS-II project file with phase data wrapped in
    """
    return project.add_phase(cif_wrap, phase_name, fmthint = 'CIF')

def find_sin_thetas(phase_lattice_parameter, hkl_list, wavelength):
    """
    #Description
    Calculate the position in two theta for a list of hkls.  Used to mark locations for fitting
    !!! Have only tested cubic crystal symmetry
    
    #Input
    phase_lattice_parameter: lattice parameter
    hkl_list: list of lattice planes (hkl)
    wavelength: dominant wavelength in the diffraction data
    
    #Returns
    List of floating point values with the position of each hkl in 2-theta
    #? Is this in radians or degrees?
    #? Returning theta or two_theta?
    """
    D=[phase_lattice_parameter/ math.sqrt(hkl[0]*hkl[0]+hkl[1]*hkl[1]+hkl[2]*hkl[2]) for hkl in hkl_list]
    SinTheta=[1*wavelength/(2*d) for d in D]
    return SinTheta

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

def get_theoretical_intensities(gpx_file_name,material,cif_file,instrument_calibration_file,G2sc,DataPathWrap,SaveWrap):
    """
    #Description
    Function to calculate the theoretical intensities. Simulated diffraction profile calculated based on the .cif file and instrument parameter file
    
    #Input
    gpx_file_name: GSAS-II datafile (ends in .gpx)
    material: Short name for the material (phase) for the dataframe e.g., 'Austenite', 'Ferrite'
    cif_file: Crystallographic Information Format file for the phase to be simulated
    instrument_calibration_file:
    G2sc: GSAS-II scriptable module.  Passed to resolve the pathway
    DataPathWrap: Path prefix to the location of the datafiles to read
    SaveWrap: Path prefix to the location where new data should be saved
    
    #Returns
    ti_table: Pandas dataframe with theoretical intensities
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
                DataPathWrap(instrument_calibration_file),5.,120.,Npoints=5000,
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
    print(ti_table)
    return ti_table

def Phase_Fraction(Merged_DataFrame):
    """
    #Description
    Calculate Phase Fraction
    
    #Input
    Merged_DataFrame: combined
    
    #Returns
    phase_dict: dictionary with phase values
    
    """
    
    # Extract all phases listed
    phase_list=Merged_DataFrame['Phase'].unique()
    
    
    phase_dict = {"Phase":[],"Mean_value":[],"StDev_value":[],"hkls":[],"Number_hkls":[]};
    
    
    for phase in phase_list:
        phase_dict["Phase"].append(phase)
        
        Phase_DF=Merged_DataFrame.loc[Merged_DataFrame['Phase'] == phase][['h','k','l','n_int']]
        phase_dict["Mean_value"].append(Phase_DF['n_int'].mean())
        phase_dict["StDev_value"].append(Phase_DF['n_int'].std())
        
        #Phase_DF['hkl']=Phase_DF.agg('{0['h']}{0['k']}{0['l']}'.format, axis=1)
        #phase_dict["hkls"].append(list(Phase_DF['hkl']))
        
        #phase_dict["Number_hkls"].append(len(list(Phase_DF['hkl'])))
        
        # For now, pandas won't create a database if terms are of different lenght
        phase_dict["hkls"].append(np.nan)
        phase_dict["Number_hkls"].append(np.nan)
    
    
    
    phase_fraction_DF=pd.DataFrame(data=phase_dict)
    
    phase_fraction_DF["Fraction"]=phase_fraction_DF["Mean_value"]/(phase_fraction_DF["Mean_value"].sum())
    
    # Dash only accepts dictionaries, not dataframes
    
    return (phase_fraction_DF.to_dict('records'), [{"name": i, "id": i} for i in phase_fraction_DF.columns])
        #['h','k','l','n_int']
    #df.loc[df['column_name'] == some_value]
