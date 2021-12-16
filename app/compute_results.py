import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

def compute(datadir,workdir,xrdml_fname,instprm_fname,G2sc):
    """
    #Description
    Truncate the calculated 2Theta range?
    
    #Input
    SinTheta:
    hist:
    
    #Output
    TwoThetaInRange:
    """
    
    #Helper functions to create full path descriptions
    DataPathWrap = lambda fil: datadir + '/' + fil
    SaveWrap = lambda fil: workdir + '/' + fil
    
    # start new GSAS-II project
    gpx = G2sc.G2Project(newgpx=SaveWrap('pkfit.gpx'))

    #Commented out format hint so that other examples work
#    hist = gpx.add_powder_histogram(DataPathWrap(xrdml_fname),
#                                    DataPathWrap(instprm_fname),
#                                    fmthint='Panalytical xrdml (xml)', databank=1, instbank=1)

    hist = gpx.add_powder_histogram(DataPathWrap(xrdml_fname),
                                    DataPathWrap(instprm_fname),
                                    databank=1, instbank=1)


    fig1 = get_figures(hist)

    
    # Change these to be passed as part of the function?
    PhaseAustenite = get_phase(DataPathWrap("austenite-Duplex.cif"), "Austenite", gpx)
    PhaseFerrite = get_phase(DataPathWrap("ferrite-Duplex.cif"), "Ferrite", gpx)

    # Read the lattice parameter 
    a0_Austenite=PhaseAustenite.data['General']['Cell'][1]
    a0_Ferrite=PhaseFerrite.data['General']['Cell'][1]

    # Find the ka1 wavelength in the file
    # works for some data files that have information encode, otherwise may need to prompt
    try:
        Ka1_wavelength=float([s for s in hist.data['Comments'] if s.startswith('Ka1')][0].split('=')[1])
    except:
        Ka1_wavelength=1.5405 # hardcoded in for now with Cu source.  Read from instrument parameter file?

    #hardcoding HKL lists for now, likely better ways to do this later...
    HKL_BCC=[[1,1,0],[2,0,0],[2,1,1],[2,2,0],[3,1,0],[2,2,2],[3,2,1],[4,1,1]]
    HKL_FCC=[[1,1,1],[2,0,0],[2,2,0],[3,1,1],[2,2,2],[4,0,0],[3,3,1],[4,2,0],[4,2,2]]
    
    SinTheta_BCC = find_sin_thetas(a0_Ferrite, HKL_BCC, Ka1_wavelength)
    SinTheta_FCC = find_sin_thetas(a0_Austenite, HKL_FCC, Ka1_wavelength)

    # Create a list of 2Theta values from the dspacing and wavelength. Mark any non-physical values with np.nan
    TwoThetaInRange_BCC=find_two_theta_in_range(SinTheta_BCC,hist)         
    TwoThetaInRange_FCC=find_two_theta_in_range(SinTheta_FCC,hist)

    PeaksList=[]
    PeaksList = np.array(TwoThetaInRange_BCC)[~np.isnan(np.array(TwoThetaInRange_BCC))]
    PeaksList = np.concatenate((PeaksList,
                            np.array(TwoThetaInRange_FCC)[~np.isnan(np.array(TwoThetaInRange_FCC))]),
                            axis=0)
    PeaksList=list(PeaksList)

    PeaksList=[x+0.5 for x in PeaksList]

    # reset the peak list in case of errors...
    hist.Peaks['peaks']=[]

    hist.set_refinements({'Background': {"no. coeffs": 5,'type': 'chebyschev-1', 'refine': True}})
    hist.refine_peaks()

    two_theta = hist.data['data'][1][0]
    h_data = hist.data['data'][1][1]
    h_background = hist.data['data'][1][4]
    h_fit = hist.data['data'][1][3]

    for peak in PeaksList:
        hist.add_peak(1, ttheta=peak)

    # Need to use this order, otherwise fitting gets unstable

    hist.set_peakFlags(area=True)
    hist.refine_peaks()
            
    hist.set_peakFlags(pos=True,area=True)
    hist.refine_peaks()

    hist.set_peakFlags(pos=True,area=True,sig=True)
    hist.refine_peaks()

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(x=two_theta,y=h_data,mode='markers',name='data'))
    fig2.add_trace(go.Scatter(x=two_theta,y=h_background,mode='markers',name='background'))
    fig2.add_trace(go.Scatter(x=two_theta,y=h_fit,mode='lines',name='fit'))

    fig2.update_layout(
        title="",
        xaxis_title="2theta",
        yaxis_title="Intensity"
    )

    # Likely move to function?  That way we also can allow more than 2 phases?
    austenite_tis = get_theoretical_intensities(gpx_file_name='Austenite-sim.gpx',
                                                material='Austenite',
                                                cif_file='austenite-Duplex.cif',
                                                test_calibration_file='TestCalibration.instprm',
                                                G2sc=G2sc,
                                                DataPathWrap=DataPathWrap,
                                                SaveWrap=SaveWrap)

    ferrite_tis = get_theoretical_intensities(gpx_file_name='Ferrite-sim.gpx',
                                              material='Ferrite',
                                              cif_file='ferrite-Duplex.cif',
                                              test_calibration_file='TestCalibration.instprm',
                                              G2sc=G2sc,
                                              DataPathWrap=DataPathWrap,
                                              SaveWrap=SaveWrap)



    #breakpoint()

    tis = pd.concat((austenite_tis,ferrite_tis),axis=0,ignore_index=True)
    tis = tis.sort_values(by='two_theta')
    tis = tis.reset_index(drop=True)
    print(tis)
  
    
    mydf = pd.DataFrame(hist.data['Peak List']['peaks'])
    mydf = mydf.iloc[:,[0,2,4,6]]
    mydf.columns = ['pos','int','sig','gam']
    mydf = mydf.sort_values('pos')
    mydf = mydf.reset_index(drop=True)
    #mydf = mydf.loc[(0 < mydf.sig) & (mydf.sig < 90),:]
    print(mydf)
    #breakpoint()

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
    
    intensity_table = mydf.to_dict('records')
    tbl_columns = [{"name": i, "id": i} for i in mydf.columns]

    return fig1, fig2, intensity_table, tbl_columns, ni_fig

def get_figures(hist):
    df = pd.DataFrame({
        "two_theta":hist.data['data'][1][0],
        "intensity":hist.data['data'][1][1]
    })

    fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')
    return fig

def get_phase(cif_wrap, phasename, project):
    return project.add_phase(cif_wrap, phasename, fmthint = 'CIF')

def find_sin_thetas(phase, hkl_list, wavelength):
    D=[phase/ math.sqrt(hkl[0]*hkl[0]+hkl[1]*hkl[1]+hkl[2]*hkl[2]) for hkl in hkl_list]
    SinTheta=[1*wavelength/(2*d) for d in D]
    return SinTheta

def find_two_theta_in_range(SinTheta, hist):
    """
    #Description
    Truncate the calculated 2Theta range?
    
    #Input
    SinTheta:
    hist:
    
    #Output
    TwoThetaInRange:
    """
    TwoTheta=[np.nan]*len(SinTheta)
    for i,value in enumerate(SinTheta):
        #print(value)
        try:
            TwoTheta[i]=(2*math.degrees(math.asin(value)))
        except:
            TwoTheta[i]=(np.nan)

    TwoThetaInRange=[np.nan if i > max(hist.data['data'][1][0]) else i for i in TwoTheta]
    TwoThetaInRange=[np.nan if i < min(hist.data['data'][1][0]) else i for i in TwoThetaInRange]
    return TwoThetaInRange

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
    
    #Output
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
