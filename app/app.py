# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import io
import os
import re

import sys
#import matplotlib.pyplot as plt
#import numpy as np
sys.path.insert(0,'/Users/dtn1/gsas2full/GSASII/') # needed to "find" GSAS-II modules
import GSASIIscriptable as G2sc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])


app.layout = dbc.Container([
        
    html.Br(),
    html.H2('Austenite Calculator'),
    html.Div('Calculating austenite since 2021.'),
    html.Br(),
    
    dbc.Tabs([
            
        dbc.Tab([
            html.Br(),
            
            # file upload
            html.Div('Use the buttons below to upload your .xrdml and .instprm files. '),
            html.Br(),
            dcc.Upload(
                    id='upload-data-xrdml',
                    children=html.Div([
                            dbc.Button('Upload .xrdml File')
                            ])),
            
            html.Br(),
            dcc.Upload(
                    id='upload-data-instprm',
                    children=html.Div([
                            dbc.Button('Upload .instprm File')
                            ])),

            # submit button
            html.Br(),
            html.Hr(),
            html.Br(),
            html.Div("""Once your files have been uploaded, click the button below
                     to begin the analysis."""),
            html.Br(),
            dbc.Button(id='submit-button-state', n_clicks=0, children='Begin Analysis')
            ],
            label="Data Upload", 
            tab_id="data_upload"),
            
            ### --- end tab 1 --- ###
        
        dbc.Tab([dcc.Graph(id='intensity-plot')],
                label="Peak Intensity Plot", 
                tab_id="peak_intensity_plot")
        ],
        id="tabs",
        active_tab="data_upload"
    ),
    
])
    
@app.callback(
        Output('intensity-plot', 'figure'),
        Input('submit-button-state', 'n_clicks'),
        State('upload-data-xrdml','contents'),
        State('upload-data-xrdml','filename'),
        State('upload-data-instprm','contents'),
        State('upload-data-instprm','filename'))
def update_output(n_clicks,
                  xrdml_contents,xrdml_fname,
                  instprm_contents,instprm_fname):
    
    # return nothing when app opens
    if n_clicks == 0:
        return go.Figure()
    
    else:
        # point towards directory and upload data using GSASII
        
        datadir = '../server_datadir'
        workdir = '../server_workdir'

        all_contents = [[xrdml_contents,xrdml_fname],
                        [instprm_contents,instprm_fname]]

        for i in range(len(all_contents)):
                contents = all_contents[i][0]
                fname = all_contents[i][1]
        
                content_type, content_string = contents.split(',')

                decoded = base64.b64decode(content_string)
                f = open(datadir + '/' + fname,'w')
                to_write = decoded.decode('utf-8')
                if re.search('instprm$',fname) is not None:
                        to_write = re.sub('\\r','',to_write)
                f.write(to_write)
                f.close()
        

        
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
        
        return the_fig

if __name__ == '__main__':
    app.run_server(debug=True)
