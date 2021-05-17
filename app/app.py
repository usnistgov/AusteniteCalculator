# -*- coding: utf-8 -*-

# dash imports
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table

# plotting
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# utils
import base64
import io
import os
import re
import sys
import flask

# user created
import compute_results

# Gsas
# sys.path.insert(0,'/Users/dtn1/gsas2full/GSASII/') # needed to "find" GSAS-II modules
sys.path.insert(0,'/g2full/GSASII/')
import GSASIIscriptable as G2sc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
server = app.server



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
        dbc.Tab([
            dcc.Graph(id='intensity-plot'),
            html.Br(),
            dcc.Graph(id='fitted-intensity-plot')
            ],
            label="Intensity Plots"),

        # Tab 3
        dbc.Tab([
            html.Br(),
            dash_table.DataTable(id='intensity-table')],
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
def show_f_name2(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded File: " + filename

@app.callback(
    Output('f4-name','children'),
    Input('upload-ferr','filename')
)
def show_f_name3(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded File: " + filename

@app.callback(
    Output('submit-confirmation','children'),
    Input('submit-button-state','n_clicks')
)
def show_f_name4(n_clicks):
    
    if n_clicks == 0:
        return ""
        
    else:
        return "Submission complete. Navigate the above tabs to view results."

### --- end file upload messages --- ###


### --- all other outputs --- ###
@app.callback(
    Output('intensity-plot','figure'),
    Output('fitted-intensity-plot','figure'),
    Output('intensity-table','data'),
    Output('intensity-table','columns'),
    Input('submit-button-state', 'n_clicks'),
    State('upload-data-xrdml','contents'),
    State('upload-data-xrdml','filename'),
    State('upload-data-instprm','contents'),
    State('upload-data-instprm','filename'),
    State('upload-aust','contents'),
    State('upload-aust','filename'),
    State('upload-ferr','contents'),
    State('upload-ferr','filename'))
def update_output(n_clicks,
                  xrdml_contents,xrdml_fname,
                  instprm_contents,instprm_fname,
                  aust_contents,aust_fname,
                  ferr_contents,ferr_fname):
    
    # return nothing when app opens
    if n_clicks == 0:
        return go.Figure(), go.Figure(), [], []

    # point towards directory and upload data using GSASII
    datadir = '../server_datadir'
    workdir = '../server_workdir'

    all_contents = [[xrdml_contents,xrdml_fname],
                    [instprm_contents,instprm_fname],
                    [aust_contents,aust_fname],
                    [ferr_contents,ferr_fname]]

    # For each uploaded file, save (on the server)
    # ensuring that the format matches what GSAS expects.
    for i in range(len(all_contents)):
        contents = all_contents[i][0]
        fname = all_contents[i][1]

        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        f = open(datadir + '/' + fname,'w')
        to_write = decoded.decode('utf-8')
        if re.search('(instprm$)|(cif)',fname) is not None:
            to_write = re.sub('\\r','',to_write)
        f.write(to_write)
        f.close()
    
    # Now, we just run the desired computations
    fig1, fig2, intensity_tbl, tbl_columns = compute_results.compute(datadir,workdir,xrdml_fname,instprm_fname,G2sc)
    
    return fig1, fig2, intensity_tbl, tbl_columns

if __name__ == '__main__':
    #app.run_server(port=8050)
    app.run_server(host='0.0.0.0',debug=True,port=8050)
