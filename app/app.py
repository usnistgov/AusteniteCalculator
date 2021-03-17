# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# dash imports
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table

# plotly, pandas
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# utils
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
    html.H1('Austenite Calculator'),
    html.Div('Calculating austenite since 2021.',style={'font-style':'italic'}),
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
                            dbc.Button('X-Ray Diffraction File (.xrdml)')
                            ])),
            html.Div(id='f1-name'),
            
            html.Br(),
            dcc.Upload(
                    id='upload-data-instprm',
                    children=html.Div([
                            dbc.Button('Instrument Parameter File (.instprm)')
                            ])),
            html.Div(id='f2-name'),

            html.Br(),
            dcc.Upload(
                    id='upload-aust',
                    children=html.Div([
                            dbc.Button('Austenite File (.cif)')
                            ])),
            html.Div(id='f3-name'),

            html.Br(),
            dcc.Upload(
                    id='upload-ferr',
                    children=html.Div([
                            dbc.Button('Ferrite File (.cif)')
                            ])),
            html.Div(id='f4-name'),

            # submit button
            html.Br(),
            html.Hr(),
            html.Br(),
            html.Div("""Once your files have been uploaded, click the button below
                     to begin the analysis."""),
            html.Br(),
            dbc.Button(id='submit-button-state', n_clicks=0, children='Begin Analysis'),
            html.Div(id='submit-confirmation')
            ],
            label="Data Upload"),
            
        ### --- end tab 1 --- ###
        
        # Tab 2
        dbc.Tab([dcc.Graph(id='intensity-plot')],
                label="Peak Intensity Plot"),

        # Tab 3
        dbc.Tab([html.Div(id='intensity-table')],
                label='Intensity Table')

    ], # end dbc.Tabs()
    id="tabs",
    active_tab="data_upload"),
    
])

### --- file upload messages --- ###
@app.callback(
    Output('f1-name','children'),
    Input('upload-data-xrdml','filename')
)
def show_f_name(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded File: " + filename

@app.callback(
    Output('f2-name','children'),
    Input('upload-data-instprm','filename')
)
def show_f_name1(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded File: " + filename

@app.callback(
    Output('f3-name','children'),
    Input('upload-aust','filename')
)
def show_f_name1(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded File: " + filename

@app.callback(
    Output('f4-name','children'),
    Input('upload-ferr','filename')
)
def show_f_name1(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded File: " + filename

@app.callback(
    Output('submit-confirmation','children'),
    Input('submit-button-state','n_clicks')
)
def show_f_name2(n_clicks):
    
    if n_clicks == 0:
        return ""
        
    else:
        return "Submission complete. Navigate the above tabs to view results."

### --- end file upload messages --- ###


### --- all other outputs --- ###
@app.callback(
    Output('intensity-plot','figure'),
    #Output('intensity-table','children'),
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
