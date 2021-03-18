def compute(datadir,workdir,xrdml_fname,instprm_fname,G2sc):

    # plotly, pandas
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

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

    the_fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')

    PhaseAustenite = gpx.add_phase(DataPathWrap("austenite-Duplex.cif"),phasename="Austenite",fmthint='CIF')

    PhaseFerrite = gpx.add_phase(DataPathWrap("ferrite-Duplex.cif"),phasename="Ferrite",fmthint='CIF')

    return the_fig