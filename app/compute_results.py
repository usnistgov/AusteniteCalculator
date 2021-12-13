import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

def compute(datadir,workdir,xrdml_fname,instprm_fname,G2sc):

    DataPathWrap = lambda fil: datadir + '/' + fil
    SaveWrap = lambda fil: workdir + '/' + fil
    gpx = G2sc.G2Project(newgpx=SaveWrap('pkfit.gpx')) # start new project
    hist = gpx.add_powder_histogram(DataPathWrap(xrdml_fname),
                                    DataPathWrap(instprm_fname),
                                    fmthint='Panalytical xrdml (xml)', databank=1, instbank=1)

    fig1 = get_figures()

    PhaseAustenite = get_phase(DataPathWrap("austenite-Duplex.cif"), "Austenite", gpx)
    PhaseFerrite = get_phase(DataPathWrap("ferrite-Duplex.cif"), "Ferrite", gpx)

    # Read the lattice parameter 
    a0_Austenite=PhaseAustenite.data['General']['Cell'][1]
    a0_Ferrite=PhaseFerrite.data['General']['Cell'][1]

    # Find the ka1 wavelength
    Ka1_wavelength=float([s for s in hist.data['Comments'] if s.startswith('Ka1')][0].split('=')[1])

    #hardcoding HKL lists for now, likely better ways to do this later...
    HKL_BCC=[[1,1,0],[2,0,0],[2,1,1],[2,2,0],[3,1,0],[2,2,2],[3,2,1],[4,1,1]]
    HKL_FCC=[[1,1,1],[2,0,0],[2,2,0],[3,1,1],[2,2,2],[4,0,0],[3,3,1],[4,2,0],[4,2,2]]
    
    SinTheta_BCC = find_sin_thetas(a0_Ferrite, HKL_BCC, Ka1_wavelength)
    SinTheta_FCC = find_sin_thetas(a0_Austenite, HKL_FCC, Ka1_wavelength)

    # Create a list of 2Theta values from the dspacing and wavelength. Mark any non-physical values with np.nan
    TwoTheta_BCC=find_two_theta_in_range(SinTheta_BCC)         
    TwoTheta_FCC=find_two_theta_in_range(SinTheta_FCC)

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

    tis = np.concatenate((austenite_tis,ferrite_tis))
    tis = pd.DataFrame({
        'R':tis,
        'phase':np.concatenate( (['Austenite']*len(austenite_tis),['Ferrite']*len(ferrite_tis)) )
    })
    
    mydf = pd.DataFrame(hist.data['Peak List']['peaks'])
    mydf = mydf.iloc[:,[0,2,4,6]]
    mydf.columns = ['pos','int','sig','gam']
    mydf = pd.concat((mydf,tis),axis=1)
    mydf['n_int'] = mydf['int']/mydf['R']
    intensity_table = mydf.to_dict('records')
    tbl_columns = [{"name": i, "id": i} for i in mydf.columns]

    ni_fig = px.scatter(mydf, x="pos", y="n_int", color="phase",
                        labels = {
                            'pos':'2-theta',
                            'n_int':'Normalized Intensity'
                            }
                        )

    return fig1, fig2, intensity_table, tbl_columns, ni_fig

def get_figures()
    df = pd.DataFrame({
        "two_theta":hist.data['data'][1][0],
        "intensity":hist.data['data'][1][1]
    })

    fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')
    return fig

def get_phase(cif_wrap, phasename, project)
    return project.add_phase(cif_wrap, phasename, fmthint = 'CIF')

def find_sin_thetas(phase, hkl_list, wavelength)
    D=[phase/ math.sqrt(hkl[0]*hkl[0]+hkl[1]*hkl[1]+hkl[2]*hkl[2]) for hkl in hkl_list]
    SinTheta=[1*wavelength/(2*d) for d in D]
    return SinTheta

def find_two_theta_in_range(SinTheta, hist)
    TwoTheta=[np.nan]*len(SinTheta)
    for i,value in enumerate(SinTheta):
        #print(value)
        try:
            TwoTheta[i]=(2*math.degrees(math.asin(value)))
        except:
            TwoTheta[i]=(np.nan)

    TwoThetaInRange=[np.nan if i > max(hist.data['data'][1][0]) else i for i in TwoTheta]
    TwoThetaInRange=[np.nan if i < min(hist.data['data'][1][0]) else i for i in TwoThetaInRange]
    return TwoTheta

def get_theoretical_intensities(gpx_file_name,material,cif_file,test_calibration_file,G2sc,DataPathWrap,SaveWrap): 

    # material: e.g., 'Austenite', 'Ferrite'

    gpx = G2sc.G2Project(newgpx=SaveWrap(gpx_file_name)) # create a project    

    Phase = gpx.add_phase(DataPathWrap(cif_file), phasename=material,fmthint='CIF')

    histogram_scale=100.

    # add a simulated histogram and link it to the previous phase(s)
    hist1 = gpx.add_simulated_powder_histogram(material + " simulation",
                DataPathWrap(test_calibration_file),5.,120.,Npoints=5000,
                phases=gpx.phases(),scale=histogram_scale)
    gpx.do_refinements()   # calculate pattern
    gpx.save()

    tis = hist1.data['Reflection Lists'][material]['RefList'][:,11]

    return tis