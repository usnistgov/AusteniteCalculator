# -*- coding: utf-8 -*-

# dash imports
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc
#from dash.dash_table.Format import Format, Scheme, Trim # Tried to set format, failed...

# plotting
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# utils
import base64
import io
import os
import platform
import re
import sys
import flask

# Add example comment

# user created
import compute_results

# Gsas
if platform.system() == 'Linux':
    sys.path.insert(0,'/root/g2full/GSASII/') # <- for Docker (assuming none of us use a Linux OS)

# David's local development (add your own line to work on the project locally)
elif re.search('dtn1',os.getcwd()):
    sys.path.insert(0,'/Users/dtn1/Anaconda3/envs/G2_2/GSASII/')

elif re.search('maxgarman',os.getcwd()):
    sys.path.insert(0,'/Users/maxgarman/opt/anaconda3/GSASII/') 

elif re.search('creuzige',os.getcwd()):
    sys.path.insert(0, '/Users/creuzige/gsas2full/envs/gsas-AustCalc/GSASII/')

elif re.search('schen',os.getcwd()):
    sys.path.insert(0, '/Users/schen/.conda/envs/conda_gsas_env/GSASII/')


import GSASIIscriptable as G2sc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
server = app.server

app.layout = dbc.Container([
        
    html.Br(),
    html.H1('Austenite Calculator'),
    html.Div('Calculating austenite since 2021.',style={'font-style':'italic'}),
    html.Br(),
    
    dbc.Tabs([
        ### --- start tab 1 --- ###
        dbc.Tab([
            html.Br(),
            
            # file upload
            html.Div('Use the buttons below to upload your .xrdml and .instprm files. ' + 
                     'Alternatively, click the "Use Default Files" button below to use a sample set of files.'),
            html.Br(),
            
            ## Button for uploading Diffraction File
            dcc.Upload(
                    id='upload-data-xrdml',
                    children=html.Div([
                            dbc.Button('X-Ray Diffraction File (.xrdml)')
                            ])),
            html.Div(id='f1-name'),
            html.Br(),
            
            ## Button for uploading Instrument Parameter File
            dcc.Upload(
                    id='upload-data-instprm',
                    children=html.Div([
                            dbc.Button('Instrument Parameter File (.instprm)')
                            ])),
            html.Div(id='f2-name'),
            html.Br(),
            
            ## Button for uploading Austenite phase file
            dcc.Upload(
                    id='upload-cif',
                    children=html.Div([
                            dbc.Button('Crystallographic Information Files (.cif)')
                            ]),
                    multiple=True),
            html.Div(id='f3-name'),

            ## Checkbox to use the default files instead
            html.Hr(),
            dbc.Checklist(
                options=[
                    {"label": "Textured Duplex Steel Example (Default, Example 01 Files)", "value": 1},
                ],
                id="default-files-check",
            ),

            ## Checkbox to use Example 05 files instead
            html.Hr(),
            dbc.Checklist(
                options=[
                    {"label": "Withdrawn SRM 487 Example (Example 05 Files)", "value": 1},
                ],
                id="example05-files-check",
            ),
            
            ## Checkbox to use Example 06 files instead
            html.Hr(),
            dbc.Checklist(
                options=[
                    {"label": "Simulated 3 Phase Example (Example 06 Files)", "value": 1},
                ],
                id="example06-files-check",
            ),
            # submit button
            html.Hr(),
            html.Div("""Once your files have been uploaded, click the button below
                     to begin the analysis."""),
            html.Br(),
            dbc.Button(id='submit-button-state', n_clicks=0, children='Begin Analysis'),
            html.Div(id='submit-confirmation'),
            html.Br(),
            html.Br(),
            html.Br()
            ],
            label="Data Upload"),
            
        ### --- end tab 1 --- ###
        
        ### --- start tab 2 --- ###
        dbc.Tab([
            html.Div("""Plot of the raw data."""),
            dcc.Graph(id='intensity-plot'),
            html.Br(),
            html.Div("""Plot of the raw data and fit.  The fit value should overlap the raw data"""),
            dcc.Graph(id='fitted-intensity-plot')
            ],
            label="Intensity Plots"),
        
        ### --- end tab 2 --- ###
        
        ### --- start tab 3 --- ###
        dbc.Tab([
            html.Br(),
            html.Div("""Table of Phase Fractions"""),
            dash_table.DataTable(id='phase-frac-table'),
            
            #? Format data output
            # Tried example from https://community.plotly.com/t/dash-table-formatting-decimal-place/34975/8, https://formattable.pythonanywhere.com/
            # But keep running into issues
            #dash_table.DataTable(id='intensity-table',format=Format(precision=2, scheme=Scheme.fixed)), #tried to set format, failed unexpeced keyword arguement 'format'
#            dash_table.DataTable(id='intensity-table',
#            columns=[
#                {
#                    "name": i,
#                    "id": i,
#                    "type": "numeric",  # Required!
#                    "format": formatted
#                }
#                for i in df.columns
#            ],
#            data=df.to_dict("records"),
#            editable=True,
#            ),
            html.Br(),
            html.Div("""Flagged Notes to Users"""),
            dash_table.DataTable(id='uncert-table'),

            html.Br(),
            html.Div("""Table of Fit and Theoretical Intensities"""),
            dash_table.DataTable(id='intensity-table'),
            #
            html.Br(),
            html.Div("""Plot of the Normalized Intensities.  The value for each phase should be constant.
                        Deviation from a constant value indicates unaccounted for factors in normalization,
                        such as texture, instrument calibration, and/or microstructure effects"""),
            dcc.Graph(id='normalized-intensity-plot'),
            
            # Graph of the two_theta values
            html.Br(),
            # Doesn't look like newlines work, but I'd like to separate this a bit more.
            html.Div("""Plot of the difference between the fit and theoretical two theta values. \n
                        Nominally all values should be near zero. \n
                        Large deviations for single peaks indicate the fit may not be correct. \n
                        Systematic deviation indicates the theoretical intensities may not be correct, or \n
                        errors in x-ray geometry."""),
            dcc.Graph(id='two_theta-plot')
            
            #Tab label
            ],
            label="Normalized intensities"),
            
            
            
        ### --- end tab 3 --- ###

    ], # end dbc.Tabs()
    id="tabs",
    active_tab="Data Upload"),
    
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
    Input('upload-cif','filename')
)
def show_f_name2(filename):
    
    if filename is None:
        return ""
        
    else:
        print(filename)
        return "Uploaded Files: " + ', '.join(filename)


@app.callback(
    Output('submit-confirmation','children'),
    Input('submit-button-state','n_clicks')
)
def show_f_name3(n_clicks):
    
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
    Output('normalized-intensity-plot','figure'),
    Output('two_theta-plot','figure'),
    Output('phase-frac-table','data'),
    Output('phase-frac-table','columns'),
    Output('uncert-table','data'),
    Output('uncert-table','columns'),
    Input('submit-button-state', 'n_clicks'),
    State('upload-data-xrdml','contents'),
    State('upload-data-xrdml','filename'),
    State('upload-data-instprm','contents'),
    State('upload-data-instprm','filename'),
    State('upload-cif','contents'),
    State('upload-cif','filename'),
    State('default-files-check','value'),
    State('example05-files-check','value'),
    State('example06-files-check','value'))
def update_output(n_clicks,
                  xrdml_contents,xrdml_fname,
                  instprm_contents,instprm_fname,
                  cif_contents,cif_fnames,
                  use_default_files, use_example05_files, use_example06_files):
    
    # return nothing when app opens
    if n_clicks == 0:
        return go.Figure(), go.Figure(), [], [], go.Figure(), go.Figure(), [], [], [], []

    # point towards directory and upload data using GSASII
    # Default data location
    print(use_default_files)

    if use_default_files not in [None, []] and use_default_files[0] == 1:
        datadir = '../server_default_datadir' 
        #datadir = '../ExampleData/Example01'
        cif_fnames = ['austenite-Duplex.cif','ferrite-Duplex.cif']
        workdir = '../server_workdir'
        xrdml_fname = 'Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper_power.xrdml'
        instprm_fname = 'TestCalibration.instprm'
        
    # Use Example05 data
    #? Need to fix the austenite cif file names.  compute_results assumes a name.  Should use uploaded names?
    #? Maybe pass like the xrdml_fnames?
    elif use_example05_files not in [None, []] and use_example05_files[0] == 1:
        datadir = '../ExampleData/Example05'
        #datadir = '../ExampleData/Example01'
        cif_fnames = ['austenite-SRM487.cif','ferrite-SRM487.cif']
        workdir = '../server_workdir'
        xrdml_fname = 'E211110-AAC-001_019-000_exported.csv'
        instprm_fname = 'BrukerD8_E211110.instprm'

    elif use_example06_files not in [None, []] and use_example06_files[0] == 1:
        datadir = '../ExampleData/Example06'
        #datadir = '../ExampleData/Example01'
        cif_fnames = ['alpha-prime-martensite-SRI.cif','epsilon-martensite-SRI.cif','austenite-SRI.cif']
        workdir = '../server_workdir'
        xrdml_fname = 'Example06_simulation_generation_data.csv'
        instprm_fname = 'BrukerD8_E211110.instprm'

    #Stores user files in a directory
    else:
        datadir = '../server_datadir'
        workdir = '../server_workdir'

        non_cif_contents = [[xrdml_contents,xrdml_fname],
                        [instprm_contents,instprm_fname]]

        # For each uploaded file, save (on the server)
        # ensuring that the format matches what GSAS expects.

        # first, read non-cif files
        for i in range(len(non_cif_contents)):
            contents = non_cif_contents[i][0]
            fname = non_cif_contents[i][1]

            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            f = open(datadir + '/' + fname,'w')
            to_write = decoded.decode('utf-8')
            if re.search('(instprm$)',fname) is not None:
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
        
    # Now, we just run the desired computations
    fig1, fig2, results_df, ni_fig, two_theta_fig, phase_frac_DF, uncert_DF = compute_results.compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc)
    
    with open('export_file.txt', 'w') as writer:
        writer.write('Phase Fraction Goes here')

    # table for plotting intensity results
    intensity_tbl, tbl_columns = compute_results.df_to_dict(results_df.round(3))

    # table for plotting phase fraction results
    phase_frac_dict, phase_frac_col = compute_results.df_to_dict(phase_frac_DF.round(3))

    # table for plotting uncertainty table
    uncert_dict, uncert_col = compute_results.df_to_dict(uncert_DF.round(3))

    return fig1, fig2, intensity_tbl, tbl_columns, ni_fig, two_theta_fig, phase_frac_dict, phase_frac_col,  uncert_dict, uncert_col

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True,port=8050) 
