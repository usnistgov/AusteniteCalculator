# -*- coding: utf-8 -*-

# dash imports
from doctest import master
from fileinput import filename
import json
from posixpath import split
from unittest import result
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_file
#from dash.dash_table.Format import Format, Scheme, Trim # Tried to set format, failed...

# plotting
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.utils as pltu

# utils
import base64
import io
import os
import platform
import re
import sys
import flask
import shutil
import fnmatch

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
app.config.suppress_callback_exceptions=True
server = app.server
root_dir = os.getcwd()

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
                            ]),
                            multiple=True),
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
            # inference method
            html.Hr(),
            html.Div("Statistical Inference Method:"),
            dbc.RadioItems(
                options=[
                    {"label": "Hierarchical Bayesian (more accurate, but slower to run)", "value": 1},
                    {"label": "Paul Mandel (less accurate, but faster to run)", "value": 2}
                ],
                value=2,
                id="inference-method",
            ),

            # submit button
            html.Hr(),
            html.Div("""Once your files have been uploaded, click the button below
                     to begin the analysis."""),
            html.Br(),
            dbc.Button(id='submit-button-state', n_clicks=0, children='Begin Analysis'),
            html.Br(),
            dcc.Store(id='store-calculations', storage_type='session'),
            html.Br(),
            dcc.Loading(
                id="loading",
                type="default",
                fullscreen=False,
                children=html.Div(id="submit-confirmation",style={'color':'#1E8449'})
            ),
            html.Br(),
            html.Br(),
            html.Br()
            ],
            label="Data Upload",
            id='Data Upload'),
            
        ### --- end tab 1 --- ###

        ### --- start tab 2 --- ###
        dbc.Tab([
            html.Div([
                'Please choose from a default .instprm file if you do not have one, and the app will create a file for you',
                dcc.Dropdown(['CuKa', 'APS 30keV 11BM', '0.7A synchrotron', '1.9A ILL D1A CW', '9m HIPD 151 deg bank TOF', '10m TOF 90deg bank'], 
                ' ', id = 'default-dropdown'),
                html.Div(id = 'default-name', style={'display':'none'}),
            ]),
            html.Br(),
            dcc.Upload(
                    id='upload-default-xrdml',
                    children=html.Div([
                            dbc.Button('X-Ray Diffraction File (.xrdml)')
                            ]),
                            multiple=True),
            html.Div(id='default-xrdml'),
            html.Br(),
            dcc.Upload(
                    id='upload-default-cif',
                    children=html.Div([
                            dbc.Button('Crystallographic Information Files (.cif)')
                            ]),
                    multiple=True),
            html.Div(id='default-cif'),
            ## Button for uploading Instrument Parameter File
            html.Br(),
            html.Div([html.Button("Download Created File", id = "download-created-file"), Download(id = "download-instprm")])
            
        ],
        label="Instrument Parameter Creation"),
        ### --- end tab 2 --- ###
        ### --- start tab 3 --- ###
        dbc.Tab([
            html.Br(),
            html.Div(id='plot-placeholder'),
            html.Br(),
            html.Div("""Plot of the raw data."""),
            dcc.Graph(id='intensity-plot'),
            html.Br(),
            html.Div("""Plot of the raw data and fit.  The fit value should overlap the raw data"""),
            dcc.Graph(id='fitted-intensity-plot')
            ],
            label="Intensity Plots"),
        
        ### --- end tab 3 --- ###
        
        ### --- start tab 4 --- ###
        dbc.Tab([
            html.Br(),
            html.Div(id='table-placeholder'),
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
            html.Br(),
            html.Button("Download as CSV", id="intensity-table-button"),
            dcc.Download(id="intensity-table-download"),
            #
            html.Br(),
            html.Br(),
            html.Div(id='graph-placeholder'),
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
            dcc.Graph(id='two_theta-plot'),
            dcc.Graph(id='pf-uncert-fig'),
            dash_table.DataTable(id='pf-uncert-table'),
            html.Br(),
            html.Br()
            
            #Tab label
            ],
            label="Normalized intensities"),
            
            
            
        ### --- end tab 4 --- ###

        ### --- start tab 5 --- ###

        dbc.Tab([
            html.Br(),
            
            dcc.Markdown(
                """
                This project is still in development. 
                When completed, we hope to have a robust method to determine the phase fraction of austenite 
                in steels with metrics on the uncertainties and recommendations on methods to reduce the uncertainty.

                To report bugs, email adam.creuziger@nist.gov.

                For more details, check out the GitHub repo [here](https://github.com/usnistgov/AusteniteCalculator),
                or click the "Download Manual" button below.
                """),
            html.Br(),
            html.Div([html.Button("Download Manual", id = "download-button"), Download(id = "download-manual")]),
            html.Br()
                    

        ],
        label="About")

    ], # end dbc.Tabs()
    id="tabs")
    
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
        return "Uploaded Files: " + ', '.join(filename)

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
    Output('default-name', 'children'),
    Input('default-dropdown', 'value')
)
def update_dropdown(value):
    if value == 'CuKa':
        return 'DefaultInstprmFiles/CuKa_default.instprm'
    elif value == 'APS 30keV 11BM':
        return 'DefaultInstprmFiles/APS30keV_default.instprm'
    elif value == '0.7A synchrotron':
        return 'DefaultInstprmFiles/0.7Asynchrotron_default.instprm'
    elif value == '1.9A ILL D1A CW':
        return 'DefaultInstprmFiles/1.9ILLD1A_default.instprm'
    elif value == '9m HIPD 151 deg bank TOF':
        return 'DefaultInstprmFiles/9mHIPD_default.instprm'
    elif value == '10m TOF 90deg bank':
        return 'DefaultInstprmFiles/10mTOF_default.instprm'

@app.callback(
    Output('default-cif','children'),
    Input('upload-default-cif','filename')
)
def show_cif_names(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded Files: " + ', '.join(filename)

@app.callback(
    Output('default-xrdml','children'),
    Input('upload-default-xrdml','filename')
)
def show_xrdml_name(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded Files: " + ', '.join(filename)

@app.callback(
    Output("download-instprm", "data"),
    Input("download-created-file", "n_clicks"),
    State("upload-default-xrdml", "contents"),
    State("upload-default-xrdml", "filename"),
    State("upload-default-cif", "contents"),
    State("upload-default-cif", "filename"),
    State("default-dropdown", "value"),
    prevent_initial_call = True
)
def download_created_instprm(n_clicks,
                            xrdml_contents, xrdml_fname,
                            cif_contents, cif_fnames,
                            instprm_contents):
    datadir = '../server_datadir'
    workdir = '../server_workdir'

    if instprm_contents == 'CuKa':
        instprm_contents = 'DefaultInstprmFiles/CuKa_default.instprm'
    elif instprm_contents == 'APS 30keV 11BM':
        instprm_contents = 'DefaultInstprmFiles/APS30keV_default.instprm'
    elif instprm_contents == '0.7A synchrotron':
        instprm_contents = 'DefaultInstprmFiles/0.7Asynchrotron_default.instprm'
    elif instprm_contents == '1.9A ILL D1A CW':
        instprm_contents = 'DefaultInstprmFiles/1.9ILLD1A_default.instprm'
    elif instprm_contents == '9m HIPD 151 deg bank TOF':
        instprm_contents = 'DefaultInstprmFiles/9mHIPD_default.instprm'
    elif instprm_contents == '10m TOF 90deg bank':
        instprm_contents = 'DefaultInstprmFiles/10mTOF_default.instprm'
    
    instprm_contents = [[xrdml_contents,xrdml_fname]]

        # For each uploaded file, save (on the server)
        # ensuring that the format matches what GSAS expects.

        # first, read non-cif files
    for i in range(len(instprm_contents)):
        contents = instprm_contents[i][0]
        fname = instprm_contents[i][1]

        content_type, content_string = contents.split(',')
        print(content_string)
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

    compute_results.create_instprm_file(datadir,workdir,xrdml_fname,instprm_contents,cif_fnames,G2sc)
    
    return send_file("created_instprm.instprm")

### --- end file upload messages --- ###

### download csvs ###
@app.callback(
    Output("intensity-table-download", "data"),
    Input("intensity-table-button", "n_clicks"),
    State('intensity-table','data'),
    prevent_initial_call=True,
)
def func(n_clicks,data):
    return dcc.send_data_frame(pd.DataFrame(data).to_csv, "intensity_table.csv")

@app.callback( 
    Output("download-manual", "data"), 
    Input("download-button", "n_clicks"),
    prevent_initial_call=True
)
def func(n_clicks):
    return send_file("austenitecalculator.pdf")

### --- all other outputs --- ###
@app.callback(
    Output('plot-placeholder', 'children'),
    Output('table-placeholder', 'children'),
    Output('graph-placeholder', 'children'),
    Output('store-calculations', 'data'),
    Output('submit-confirmation','children'),
    Input('submit-button-state', 'n_clicks'),
    State('upload-data-xrdml','contents'),
    State('upload-data-xrdml','filename'),
    State('upload-data-instprm','contents'),
    State('upload-data-instprm','filename'),
    State('upload-cif','contents'),
    State('upload-cif','filename'),
    State('default-files-check','value'),
    State('example05-files-check','value'),
    State('example06-files-check','value'),
    State('inference-method','value'),
    prevent_initial_call = True
)
def update_output(n_clicks,
                  xrdml_contents,xrdml_fnames,
                  instprm_contents,instprm_fname,
                  cif_contents,cif_fnames,
                  use_default_files, use_example05_files, use_example06_files,inference_method_value):
    
    
    # point towards directory and upload data using GSASII
    # Default data location
    print(use_default_files)

    if inference_method_value == 1:
        inference_method = 'bayes'
    elif inference_method_value == 2:
        inference_method = 'paul_mandel'

    if use_default_files not in [None, []] and use_default_files[0] == 1:
        datadir = '../server_default_datadir' 
        #datadir = '../ExampleData/Example01'
        cif_fnames = ['austenite-Duplex.cif','ferrite-Duplex.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper_power.xrdml']
        instprm_fname = 'TestCalibration.instprm'
        
    # Use Example05 data
    #? Need to fix the austenite cif file names.  compute_results assumes a name.  Should use uploaded names?
    #? Maybe pass like the xrdml_fnames?
    elif use_example05_files not in [None, []] and use_example05_files[0] == 1:
        datadir = '../ExampleData/Example05'
        #datadir = '../ExampleData/Example01'
        cif_fnames = ['austenite-SRM487.cif','ferrite-SRM487.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['E211110-AAC-001_019-000_exported.csv']
        instprm_fname = 'BrukerD8_E211110.instprm'

    elif use_example06_files not in [None, []] and use_example06_files[0] == 1:
        datadir = '../ExampleData/Example06'
        #datadir = '../ExampleData/Example01'
        cif_fnames = ['alpha-prime-martensite-SRI.cif','epsilon-martensite-SRI.cif','austenite-SRI.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['Example06_simulation_generation_data.csv']
        instprm_fname = 'BrukerD8_E211110.instprm'

    #Stores user files in a directory
    else:
        datadir = '../server_datadir'
        workdir = '../server_workdir'

        # For each uploaded file, save (on the server)
        # ensuring that the format matches what GSAS expects.

        # first, read non-cif files

        instprm_type, instprm_string = instprm_contents.split(',')

        decoded = base64.b64decode(instprm_string)
        f = open(datadir + '/' + instprm_fname,'w')
        to_write = decoded.decode('utf-8')
        if re.search('(instprm$)',instprm_fname) is not None:
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
        
        for i in range(len(xrdml_contents)):
            contents = xrdml_contents[i]
            fname = xrdml_fnames[i]
            
            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            f = open(datadir + '/' + fname,'w')
            to_write = decoded.decode('utf-8')
            to_write = re.sub('\\r','',to_write)
            f.write(to_write)
            f.close()
    
    results_table = {}
    phase_frac = {}
    two_thetas = {}
    uncert = {}
    pf_uncerts = {}
    pf_uncert_table = {}
    ti_tables = {}
    altered_results = {}
    altered_phase = {}
    altered_ti = {}
    fit_points = {}
    # Now, we just run the desired computations
    for x in range(len(xrdml_fnames)):
        fit_data, results_df, phase_frac_DF, two_theta, tis, uncert_DF, pf_uncertainties, pf_uncertainty_table = compute_results.compute(datadir,workdir,xrdml_fnames[x],instprm_fname,cif_fnames,G2sc,inference_method)
        temp_string = 'Dataset: ' + str(x + 1)

        results_table[temp_string] = results_df
        phase_frac[temp_string] = phase_frac_DF
        two_thetas[temp_string] = two_theta.tolist()
        ti_tables[temp_string] = tis
        uncert[temp_string] = uncert_DF
        pf_uncerts[temp_string] = pf_uncertainties
        pf_uncert_table[temp_string] = pf_uncertainty_table
        altered_results[temp_string] = results_df
        altered_phase[temp_string] = phase_frac_DF
        altered_ti[temp_string] = tis
        fit_points[temp_string] = fit_data
        
    
    with open('export_file.txt', 'w') as writer:
        writer.write('Phase Fraction Goes here')
    
    # table for plotting intensity results
    for key, value in results_table.items():
        intensity_tbl, tbl_columns = compute_results.df_to_dict(value.round(3))
        results_table[key] = (intensity_tbl, tbl_columns)

    # table for plotting phase fraction results
    for key, value in phase_frac.items():
        phase_frac_dict, phase_frac_col = compute_results.df_to_dict(value.round(3))
        phase_frac[key] = (phase_frac_dict, phase_frac_col)

    # table for plotting uncertainty table
    for key, value in uncert.items():
        uncert_dict, uncert_col = compute_results.df_to_dict(value.round(3))
        uncert[key] = (uncert_dict, uncert_col)

    # table for plotting pf uncertainties
    for key, value in pf_uncert_table.items():
        pfu_dict, pfu_col = compute_results.df_to_dict(value.round(5))
        pf_uncert_table[key] = (pfu_dict, pfu_col)

    for key, value in ti_tables.items():
        ti_dict, ti_cols = compute_results.df_to_dict(value.round(5))
        ti_tables[key] = (ti_dict, ti_cols)

    for key, value in altered_results.items():
        res_table, res_col = compute_results.df_to_dict(value.round(3))
        res_table = value.to_dict('dict')
        altered_results[key] = (res_table, res_col)

    for key, value in altered_phase.items():
        phase_table, phase_col = compute_results.df_to_dict(value.round(3))
        phase_table = value.to_dict('dict')
        altered_phase[key] = (phase_table, phase_col)

    for key, value in altered_ti.items():
        ti_tbl, ti_col = compute_results.df_to_dict(value.round(3))
        ti_tbl = value.to_dict('dict')
        altered_ti[key] = (ti_tbl, ti_col)
    
    for key, value in pf_uncerts.items():
        value['unique_phase_names'] = value['unique_phase_names'].tolist()
        value['summary_table'] = value['summary_table'].to_dict('dict')
        saved_list = []
        for current_phase in range(len(value['mu_df'])):
            for index in range(len(value['mu_df'][current_phase])):
                temp_list = [value['mu_df'][current_phase].iloc[index, 0], value['mu_df'][current_phase].iloc[index, 1]]
                saved_list.append(temp_list)
        value['mu_df'] = saved_list
        
    master_dict = {
        'results_table':results_table,
        'phase_frac':phase_frac,
        'two_thetas':two_thetas,
        'ti_tables':ti_tables,
        'uncert':uncert,
        'pf_uncerts':pf_uncerts,
        'pf_uncert_table':pf_uncert_table,
        'altered_results':altered_results,
        'altered_phase':altered_phase,
        'altered_ti':altered_ti,
        'fit_points':fit_points
    }
    
    plot_dropdown = html.Div([
        'Please select a dataset to view',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))], id = 'plot-dropdown')
    ])

    table_dropdown = html.Div([
        'Please select a dataset to view',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))], id = 'table-dropdown')
    ])

    graph_dropdown = html.Div([
        'Please select a dataset to view',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))], id = 'graph-dropdown')
    ])

    conf = "Submission complete. Navigate the above tabs to view results."

    return (plot_dropdown,
            table_dropdown,
            graph_dropdown,
            master_dict,
            conf)

@app.callback(
    Output('intensity-plot', 'figure'),
    Output('fitted-intensity-plot', 'figure'),
    Input('store-calculations', 'data'),
    Input('plot-dropdown', 'value'),
    prevent_initial_call=True
)
def update_figures(data, value):
    fit_data = data.get('fit_points').get(value)
    current_two_theta = data.get('two_thetas').get(value)

    df = pd.DataFrame({
        "two_theta":current_two_theta,
        "intensity":fit_data[0]
    })

    raw_fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')

    fig_fit_hist = go.Figure()

    fig_fit_hist.add_trace(go.Scatter(x=current_two_theta,y=fit_data[0],mode='markers',name='data'))
    fig_fit_hist.add_trace(go.Scatter(x=current_two_theta,y=fit_data[1],mode='markers',name='background'))
    fig_fit_hist.add_trace(go.Scatter(x=current_two_theta,y=fit_data[2],mode='lines',name='fit'))

    fig_fit_hist.update_layout(
        title="",
        xaxis_title="2theta",
        yaxis_title="Intensity"
    )

    return raw_fig, fig_fit_hist

@app.callback(
    Output('intensity-table','data'),
    Output('intensity-table','columns'),
    Output('phase-frac-table','data'),
    Output('phase-frac-table','columns'),
    Output('uncert-table','data'),
    Output('uncert-table','columns'),
    Input('store-calculations', 'data'),
    Input('table-dropdown', 'value'),
    prevent_initial_call=True
)
def update_tables(data, value):
    table = data.get('results_table').get(value)[0]
    cols = data.get('results_table').get(value)[1]
    frac_table = data.get('phase_frac').get(value)[0]
    frac_cols = data.get('phase_frac').get(value)[1]
    uncert_table = data.get('uncert').get(value)[0]
    uncert_cols = data.get('uncert').get(value)[1]

    return table, cols, frac_table, frac_cols, uncert_table, uncert_cols

@app.callback(
    Output('normalized-intensity-plot','figure'),
    Output('two_theta-plot','figure'),
    Output('pf-uncert-fig','figure'),
    Output('pf-uncert-table','data'),
    Output('pf-uncert-table','columns'),
    Input('store-calculations', 'data'),
    Input('graph-dropdown', 'value'),
    prevent_initial_call=True
)
def update_graphs(data, value):
    table = data.get('altered_results').get(value)[0]
    cols = data.get('altered_results').get(value)[1]
    big_df = pd.DataFrame.from_dict(table)

    ti_table = data.get('altered_ti').get(value)[0]
    ti_cols = data.get('altered_ti').get(value)[1]
    ti_df = pd.DataFrame.from_dict(ti_table)

    pf_table = data.get('altered_phase').get(value)[0]
    pf_cols = data.get('altered_phase').get(value)[1]
    pf_df = pd.DataFrame.from_dict(pf_table)

    current_two_theta = data.get('two_thetas').get(value)

    pf_uncertainties = data.get('pf_uncerts').get(value)

    remade_df = pd.DataFrame(pf_uncertainties['mu_df'], columns=['which_phase', 'value'])
    pf_uncertainties['mu_df'] = remade_df

    pf_uncert_table = data.get('pf_uncert_table').get(value)[0]
    pf_uncert_cols = data.get('pf_uncert_table').get(value)[1]

    norm_int_plot = compute_results.create_norm_intensity_graph(big_df, ti_df, pf_df, current_two_theta)
    two_theta_diff_plot = compute_results.two_theta_compare_figure(big_df)
    pf_uncert_fig = compute_results.get_pf_uncertainty_fig(pf_uncertainties)
    
    return norm_int_plot, two_theta_diff_plot, pf_uncert_fig, pf_uncert_table, pf_uncert_cols

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True,port=8050) 

@server.route("/AusteniteCalculator/app/")
def download():
    return flask.send_from_directory(root_dir, "austenitecalculator.pdf")

@server.route("/AusteniteCalculator/server_datadir/DefaultInstprmFiles/")
def download_instprm():
    return flask.send_from_directory("/AusteniteCalculator/server_datadir/DefaultInstprmFiles/", find_file("*(edit).txt", "../server_datadir/DefaultInstprmFiles/"))

def find_file(pattern, path):
    result = None
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result