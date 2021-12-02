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


    
    df = pd.DataFrame({
        "two_theta":hist.data['data'][1][0],
        "intensity":hist.data['data'][1][1]
    })

    fig1 = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')

    PhaseAustenite = gpx.add_phase(DataPathWrap("austenite-Duplex.cif"),phasename="Austenite",fmthint='CIF')
    PhaseFerrite = gpx.add_phase(DataPathWrap("ferrite-Duplex.cif"),phasename="Ferrite",fmthint='CIF')

    # Read the lattice parameter 
    a0_Austenite=PhaseAustenite.data['General']['Cell'][1]
    a0_Ferrite=PhaseFerrite.data['General']['Cell'][1]

    # Find the ka1 wavelength
    Ka1_wavelength=float([s for s in hist.data['Comments'] if s.startswith('Ka1')][0].split('=')[1])

    #hardcoding HKL lists for now, likely better ways to do this later...
    HKL_BCC=[[1,1,0],[2,0,0],[2,1,1],[2,2,0],[3,1,0],[2,2,2],[3,2,1],[4,1,1]]
    HKL_FCC=[[1,1,1],[2,0,0],[2,2,0],[3,1,1],[2,2,2],[4,0,0],[3,3,1],[4,2,0],[4,2,2]]
    
    d_BCC=[a0_Ferrite/ math.sqrt(hkl[0]*hkl[0]+hkl[1]*hkl[1]+hkl[2]*hkl[2]) for hkl in HKL_BCC]
    SinTheta_BCC=[1*Ka1_wavelength/(2*d) for d in d_BCC]

    d_FCC=[a0_Austenite/ math.sqrt(hkl[0]*hkl[0]+hkl[1]*hkl[1]+hkl[2]*hkl[2]) for hkl in HKL_FCC]
    SinTheta_FCC=[1*Ka1_wavelength/(2*d) for d in d_FCC]

    # Create a list of 2Theta values from the dspacing and wavelength. Mark any non-physical values with np.nan
    TwoTheta_BCC=[np.nan]*len(SinTheta_BCC)
    for i,value in enumerate(SinTheta_BCC):
        #print(value)
        try:
            TwoTheta_BCC[i]=(2*math.degrees(math.asin(value)))
        except:
            TwoTheta_BCC[i]=(np.nan)    
            
    TwoTheta_FCC=[np.nan]*len(SinTheta_FCC)
    for i,value in enumerate(SinTheta_FCC):
        #print(value)
        try:
            TwoTheta_FCC[i]=(2*math.degrees(math.asin(value)))
        except:
            TwoTheta_FCC[i]=(np.nan)

    TwoThetaInRange_BCC=[np.nan if i > max(hist.data['data'][1][0]) else i for i in TwoTheta_BCC]
    TwoThetaInRange_BCC=[np.nan if i < min(hist.data['data'][1][0]) else i for i in TwoThetaInRange_BCC]

    TwoThetaInRange_FCC=[np.nan if i > max(hist.data['data'][1][0]) else i for i in TwoTheta_FCC]
    TwoThetaInRange_FCC=[np.nan if i < min(hist.data['data'][1][0]) else i for i in TwoThetaInRange_FCC]

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

    mydf = pd.DataFrame(hist.data['Peak List']['peaks'])
    mydf = mydf.iloc[:,[0,2,4,6]]
    mydf.columns = ['pos','int','sig','gam']
    intensity_table = mydf.to_dict('records')
    tbl_columns = [{"name": i, "id": i} for i in mydf.columns]

    ### calculate theoretical intensities (Austenite) ###
    gpx = G2sc.G2Project(newgpx=SaveWrap('Austenite-sim.gpx')) # create a project    

    PhaseAustenite = gpx.add_phase(DataPathWrap("austenite-Duplex.cif"), phasename="Austenite",fmthint='CIF')

    histogram_scale=100.

    # add a simulated histogram and link it to the previous phase(s)
    hist1 = gpx.add_simulated_powder_histogram("Austenite simulation",
            DataPathWrap('../server_datadir/TestCalibration.instprm'),5.,120.,Npoints=5000,
            phases=gpx.phases(),scale=histogram_scale)

    gpx.do_refinements()   # calculate pattern
    gpx.save()

    theoretical_intensities = hist1.data['Reflection Lists']['Austenite']['RefList'][:,11]
    ### end calculation of theoretical intensities ###

    return fig1, fig2, intensity_table, tbl_columns