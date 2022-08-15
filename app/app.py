# -*- coding: utf-8 -*-

# dash imports
from doctest import master
from fileinput import filename
import json
from posixpath import split
from ssl import create_default_context
from unittest import result
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_unload_component as duc
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_file

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
import glob
import random
from apscheduler.schedulers.background import BackgroundScheduler

# Add example comment

# user created
import compute_results
import compute_uncertainties

# Gsas
if platform.system() == 'Linux':
    sys.path.insert(0,'/root/g2full/GSASII/') # <- for Docker (assuming none of us use a Linux OS)

# David's local development (add your own line to work on the project locally)
elif re.search('dtn1',os.getcwd()):
    sys.path.insert(0,'/Users/dtn1/Anaconda3/envs/gsas-AustCalc/GSASII/')

elif re.search('maxgarman',os.getcwd()):
    sys.path.insert(0,'/Users/maxgarman/opt/anaconda3/GSASII/') 

elif re.search('creuzige',os.getcwd()):
    sys.path.insert(0, '/Users/creuzige/gsas2full/envs/gsas-AustCalc/GSASII/')

elif re.search('schen',os.getcwd()):
    sys.path.insert(0, '/Users/schen/.conda/envs/conda_gsas_env/GSASII/')


import GSASIIscriptable as G2sc

def clear_directory():
    dirs = glob.glob("calculator_report*/")
    for dir in dirs:
        shutil.rmtree(dir)
    zips = glob.glob("report*")
    for zip in zips:
        os.remove(zip)

scheduler = BackgroundScheduler()
scheduler.add_job(clear_directory, 'interval', hours=24)
scheduler.start()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
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
            html.Div("Statistical Inference Option:"),
            dbc.RadioItems(
                options=[
                    {"label": "Perform statistical inference (MCMC)", "value": 1},
                    {"label": "Skip the inference for now", "value": 2}
                ],
                value=1,
                id="inference-method",
            ),

            # submit button
            html.Hr(),
            html.Div("""Once your files have been uploaded, click the button below
                     to begin the analysis."""),
            html.Br(),
            dbc.Button(id='submit-button-state', n_clicks=0, children='Begin Analysis'), 
            html.Br(),
            html.Br(),
            dbc.Button(id='report-button', children='Download Analysis Report'),
            Download(id='download-full-report'),
            html.Br(),
            dcc.Store(id='store-calculations', storage_type='session'),
            html.Br(),
            dcc.Loading(
                id="loading",
                type="default",
                fullscreen=False,
                children=html.Div(id="submit-confirmation",style={'color':'#1E8449'})
            ),
            duc.Unload(id='page-listener'),
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
            html.Div(id='plot-placeholder',children=[ 
                dcc.Dropdown(options = ['Dataset: 1'], 
                            id = 'plot-dropdown',
                            value='Dataset: 1')
             ]),
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
            html.Div(id='table-placeholder',children=[ 
                dcc.Dropdown(options = ['Dataset: 1'], 
                            id = 'table-dropdown',
                            value='Dataset: 1')
             ]),
            html.Br(),
            html.Div("""Table of Phase Fractions"""),
            dash_table.DataTable(id='phase-frac-table'),
            
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
            html.Div(id='norm-int-placeholder',children=[ 
                dcc.Dropdown(options = ['Dataset: 1'], 
                            id = 'norm-int-dropdown',
                            value='Dataset: 1')
             ]),
            html.Br(),
            html.Div("""Plot of the Normalized Intensities.  The value for each phase should be constant.
                        Deviation from a constant value indicates unaccounted for factors in normalization,
                        such as texture, instrument calibration, and/or microstructure effects"""),
            dcc.Graph(id='normalized-intensity-plot'),
            html.Br(),
            html.Div(id='graph-placeholder',children=[ 
                dcc.Dropdown(options = ['Dataset: 1'], 
                            id = 'graph-dropdown',
                            value='Dataset: 1')
             ]),
            html.Br(),
            # Graph of the two_theta values
            
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
    Output('norm-int-placeholder', 'children'),
    Output('store-calculations', 'data'),
    Output('submit-confirmation','children'),
    Output('pf-uncert-fig','figure'),
    Output('pf-uncert-table','data'),
    Output('pf-uncert-table','columns'),
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
    '''Callback for the "Begin Analysis" button, runs our expensive compute_results function

    Args:
       n_clicks: button clicks
       xrdml_contents: contents for x-ray diffraction files
       xrdml_fnames: list of names for x-ray diffraction files
       instprm_contents: contents for instrument parameter file
       instprm_fname: name of instrument parameter file
       cif_contents: contents for .cif files
       cif_fnames: list of names for .cif files
       use_default_files: checkbox to use example data 1
       use_example05_files: checkbox to use example data 5
       use_example06_files: checkbox to use example data 6
       inference_method_value: selection for statistical inference method

    Returns:
        plot_dropdown: dropdown created for the raw and fit data graphs
        table_dropdown: dropdown created for the norm_int table and phase_frac table
        graph_dropdown: dropdown created for the difference in theo_int graph and phase_frac variation graph
        norm_int_dropdown: dropdown for the variation in normalized intensity graph
        master_dict: dictionary created to store data from compute_results
        conf: return to show that app is done loading

    Raises:
       
    '''
    
    # point towards directory and upload data using GSASII
    # Default data location
    print(use_default_files)

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
    ti_tables = {}
    altered_results = {}
    altered_phase = {}
    altered_ti = {}
    fit_points = {}
    #create the above dicts to store data returned from compute_results
    for x in range(len(xrdml_fnames)):
        fit_data, results_df, phase_frac_DF, two_theta, tis, uncert_DF,  = compute_results.compute(datadir,workdir,xrdml_fnames[x],instprm_fname,cif_fnames,G2sc)
        temp_string = 'Dataset: ' + str(x + 1)

        #store data in their respective dictionaries, with the keys being the current dataset(1,2,...) and the value being data
        #some are duplicated because they needed to be converted in multiple ways
        results_table[temp_string] = results_df
        phase_frac[temp_string] = phase_frac_DF
        two_thetas[temp_string] = two_theta.tolist()
        ti_tables[temp_string] = tis
        uncert[temp_string] = uncert_DF
        altered_results[temp_string] = results_df
        altered_phase[temp_string] = phase_frac_DF
        altered_ti[temp_string] = tis
        fit_points[temp_string] = fit_data

    # run MCMC using full results
    
    if inference_method_value == 1:
    
        stan_fit, unique_phases = compute_uncertainties.run_stan(results_table)
        pf_figure, pf_table = compute_uncertainties.generate_pf_plot_and_table(stan_fit,unique_phases)
        pf_uncert_table, pf_uncert_table_columns = compute_results.df_to_dict(pf_table.round(4))

    elif inference_method_value == 2:
        stan_fit, unique_phases = None, None
        pf_figure = go.Figure()
        pf_uncert_table, pf_uncert_table_columns = None, None
    
    with open('export_file.txt', 'w') as writer:
        writer.write('Phase Fraction Goes here')
    
    # convert Dataframes to dictionaries, and save the table and cols in a tuple
    for key, value in results_table.items():
        intensity_tbl, tbl_columns = compute_results.df_to_dict(value.round(3))
        results_table[key] = (intensity_tbl, tbl_columns)

    for key, value in phase_frac.items():
        phase_frac_dict, phase_frac_col = compute_results.df_to_dict(value.round(3))
        phase_frac[key] = (phase_frac_dict, phase_frac_col)

    for key, value in uncert.items():
        uncert_dict, uncert_col = compute_results.df_to_dict(value.round(3))
        uncert[key] = (uncert_dict, uncert_col)

    for key, value in ti_tables.items():
        ti_dict, ti_cols = compute_results.df_to_dict(value.round(5))
        ti_tables[key] = (ti_dict, ti_cols)

    #convert duplicate dataframes to different format(df_to_dict('dict') rather than 'records')
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
        
    master_dict = {
        'results_table':results_table,
        'phase_frac':phase_frac,
        'two_thetas':two_thetas,
        'ti_tables':ti_tables,
        'uncert':uncert,
        'altered_results':altered_results,
        'altered_phase':altered_phase,
        'altered_ti':altered_ti,
        'fit_points':fit_points
    }
    
    #create html components to replace the placeholders in the app
    plot_dropdown = html.Div([
        'Please select a dataset to view',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))] + ['View all datasets'], 
                    id = 'plot-dropdown',
                    value = 'Dataset: 1')
    ])

    norm_int_dropdown = html.Div([
        'Please select a dataset to view',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))] + ['View all datasets'], 
                     id = 'norm-int-dropdown',
                     value="Dataset: 1")
    ])

    table_dropdown = html.Div([
        'Please select a dataset to view',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))], 
                     id = 'table-dropdown',
                     value='Dataset: 1')
    ])

    graph_dropdown = html.Div([
        'Please select a dataset to view',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))], 
                     id = 'graph-dropdown',
                     value='Dataset: 1')
    ])

    conf = "Submission complete. Navigate the above tabs to view results."

    return (plot_dropdown,
            table_dropdown,
            graph_dropdown,
            norm_int_dropdown,
            master_dict,
            conf,
            pf_figure,
            pf_uncert_table,
            pf_uncert_table_columns)

@app.callback(
    Output('intensity-plot', 'figure'),
    Output('fitted-intensity-plot', 'figure'),
    Input('store-calculations', 'data'),
    Input('plot-dropdown', 'value'),
    prevent_initial_call = True
)
def update_figures(data, value):
    
    
    '''
    Args:
        data: data saved in dcc.Store from running compute_results
        value: dataset selected from dropdown

    Returns:
        raw_fig: raw data figure dynamically created in callback
        fig_fit_hist: fit data figure dynamically created in callback

    Raises:
        
    '''
    if data is None:
        return go.Figure(), go.Figure()

    fit_data = data.get('fit_points').get(value)
    current_two_theta = data.get('two_thetas').get(value)
    
    #option to select all datasets
    if value == 'View all datasets':
        created_raw = []
        created_fit = []
        for key, data_value in data.get('fit_points').items():
            current_two_theta = data.get('two_thetas')[key]
            
            raw_fig = go.Figure()
            raw_fig.add_trace(go.Scatter(x=current_two_theta,y=data_value[0],mode='lines',name='data: ' + str(key)))
            created_raw.append(raw_fig)

            fig_fit_hist = compute_results.create_fit_fig(current_two_theta, data_value, key)
            created_fit.append(fig_fit_hist)

        #graph data can be added together as tuples
        raw_graph_data = ()
        fit_graph_data = ()
        for i in range(len(created_raw)):
            raw_graph_data += created_raw[i].data
            fit_graph_data += created_fit[i].data

        big_raw = go.Figure(raw_graph_data)
        big_fit = go.Figure(fit_graph_data)
        return big_raw, big_fit
    else:
        #select a specific dataset from the dropdown
        fit_data = data.get('fit_points').get(value)
        current_two_theta = data.get('two_thetas').get(value)

        df = pd.DataFrame({
            "two_theta":current_two_theta,
            "intensity":fit_data[0]
        })

        raw_fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')

        fig_fit_hist = compute_results.create_fit_fig(current_two_theta, fit_data, value)

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
    prevent_initial_call = True
)
def update_tables(data, value):

    if data is None:
        return [], [], [], [], [], []

    """shuffle through tables using created dropdown

    Args:
        data: data saved in dcc.Store from running compute_results
        value: dataset selected from dropdown

    Returns:
       table: table of normalized intensities 
       cols: cols for normalized intensities data
       frac_table: table of phase fractions
       frac_cols: cols for phase fractions data
       uncert_table: table of flags for users
       uncert_cols: cols of user flags data

    Raises:
        
    """
    table = data.get('results_table').get(value)[0]
    cols = data.get('results_table').get(value)[1]
    frac_table = data.get('phase_frac').get(value)[0]
    frac_cols = data.get('phase_frac').get(value)[1]
    uncert_table = data.get('uncert').get(value)[0]
    uncert_cols = data.get('uncert').get(value)[1]

    return table, cols, frac_table, frac_cols, uncert_table, uncert_cols

@app.callback(
    Output('two_theta-plot','figure'),
    Input('store-calculations', 'data'),
    Input('graph-dropdown', 'value'),
    prevent_initial_call = True
)
def update_graphs(data, value):

    if data is None:
        return go.Figure()

    table = data.get('altered_results').get(value)[0]
    cols = data.get('altered_results').get(value)[1]
    big_df = pd.DataFrame.from_dict(table)
    """Shuffle through two_theta difference and phase_frac variation graphs

    Args:
        data: data saved in dcc.Store from running compute_results
        value: dataset selected from dropdown

    Returns:
        two_theta_diff_plot: plot of differences in two_theta created dynamically
        pf_uncert_fig: variation in phase_frac plot
        pf_uncert_table: table of phase_frac variation data
        pf_uncert_cols: cols of pf_uncert_table

    Raises:
        
    """
    table = data.get('altered_results').get(value)[0]
    big_df = pd.DataFrame.from_dict(table)

    two_theta_diff_plot = compute_results.two_theta_compare_figure(big_df)
    
    return two_theta_diff_plot

@app.callback(
    Output('normalized-intensity-plot','figure'),
    Input('store-calculations', 'data'),
    Input('norm-int-dropdown', 'value'),
    prevent_initial_call = True
)
def update_norm_int(data, value):
    """Shuffle through difference in norm_int plot

    Args:
        data: data saved in dcc.Store from running compute_results
        value: dataset selected from dropdown

    Returns:
        norm_int_plot: plot of variation in normalized intensities created dynamically

    Raises:
        
    """
    if data is None:
        return go.Figure()

    #option to view all datasets in one graph
    if value == 'View all datasets':
        created_plots = []
        for key, data_value in data.get('altered_results').items():
            big_df = pd.DataFrame.from_dict(data_value[0])

            ti_table = data.get('altered_ti')[key][0]
            ti_df = pd.DataFrame.from_dict(ti_table)

            pf_table = data.get('altered_phase')[key][0]
            pf_df = pd.DataFrame.from_dict(pf_table)

            current_two_theta = data.get('two_thetas')[key]

            temp_plot = compute_results.create_norm_intensity_graph(big_df, ti_df, pf_df, current_two_theta, key)
            created_plots.append(temp_plot)

        #graph data can be added together as tuples
        big_fig_data = ()
        for i in range(len(created_plots)):
            big_fig_data += created_plots[i].data

        big_fig = go.Figure(big_fig_data)
        return big_fig
    else:
        #option to select a single dataset
        table = data.get('altered_results').get(value)[0]
        big_df = pd.DataFrame.from_dict(table)

        ti_table = data.get('altered_ti').get(value)[0]
        ti_df = pd.DataFrame.from_dict(ti_table)

        pf_table = data.get('altered_phase').get(value)[0]
        pf_df = pd.DataFrame.from_dict(pf_table)

        current_two_theta = data.get('two_thetas').get(value)

        norm_int_plot = compute_results.create_norm_intensity_graph(big_df, ti_df, pf_df, current_two_theta, value)

        return norm_int_plot

@app.callback(
    Output('download-full-report', 'data'),
    Input('store-calculations', 'data'),
    Input('report-button', 'n_clicks'),
    State('upload-data-xrdml','contents'),
    State('upload-data-xrdml','filename'),
    State('upload-data-instprm','contents'),
    State('upload-data-instprm','filename'),
    State('upload-cif','contents'),
    State('upload-cif','filename'),
    State('default-files-check','value'),
    State('example05-files-check','value'),
    State('example06-files-check','value'),
    prevent_initial_call=True
)
def create_zip_report(data, n_clicks, 
                    xrdml_contents,xrdml_fnames,
                    instprm_contents,instprm_fname,
                    cif_contents,cif_fnames,
                    use_default_files, use_example05_files, use_example06_files):
    """create and send a .zip file of a report with the calculated data 
    Args:
        data: data saved in dcc.Store from running compute_results
        n_clicks: button clicks

    Returns:
        send_file('report.zip'): send created .zip file to be downloaded

    Raises:
        
    """
    hash = random.randrange(10000)
    if data == None or n_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    temp_path = os.path.join(root_dir, 'calculator_report' + str(hash))

    os.mkdir(temp_path)

    send_input=True

    if use_default_files not in [None, []] and use_default_files[0] == 1:
        send_input=False
    elif use_example05_files not in [None, []] and use_example05_files[0] == 1:
        send_input=False
    elif use_example06_files not in [None, []] and use_example06_files[0] == 1:
        send_input=False
    #make directory for each dataset
    for creation_key, dataset_value in data.get('results_table').items():
        dataset_path = os.path.join(temp_path, creation_key)
        if not(os.path.isdir(dataset_path)):
            os.mkdir(dataset_path)
            
    #make raw and fit data figures
    for key, value in data.get('fit_points').items():
        current_two_theta = data.get('two_thetas')[key]

        temp_df = pd.DataFrame({
        "two_theta":current_two_theta,
        "intensity":value[0]
        })

        raw_fig = px.line(temp_df,x='two_theta',y='intensity',title='Peak Fitting Plot')

        fig_fit_hist = compute_results.create_fit_fig(current_two_theta, value, key)

        #send figs to pdfs
        raw_fig.write_image(os.path.join(temp_path, key, 'raw_data.pdf'))
        fig_fit_hist.write_image(os.path.join(temp_path, key, 'fit_data.pdf'))

    #get tables and send to .csv files
    for key, value in data.get('results_table').items():
        results_df = pd.DataFrame.from_dict(value[0])
        results_df.to_csv(os.path.join(temp_path, key, 'norm_int.csv'))
    
    for key, value in data.get('phase_frac').items():
        phase_frac_df = pd.DataFrame.from_dict(value[0])
        phase_frac_df.to_csv(os.path.join(temp_path, key, 'phase_frac.csv'))

    for key, value in data.get('pf_uncerts').items():
        remade_df = pd.DataFrame(value['mu_df'], columns=['which_phase', 'value'])
        value['mu_df'] = remade_df

        pf_uncert_fig = compute_results.get_pf_uncertainty_fig(value)
        pf_uncert_fig.write_image(os.path.join(temp_path, key, 'pf_uncert_fig.pdf'))

    for key, value in data.get('altered_results').items():
        big_table = value[0]
        big_df = pd.DataFrame.from_dict(big_table)

        altered_ti = data.get('altered_ti')[key][0]
        ti_df = pd.DataFrame.from_dict(altered_ti)

        altered_phase = data.get('altered_phase')[key][0]
        phase_df = pd.DataFrame.from_dict(altered_phase)

        current_two_theta = data.get('two_thetas')[key]

        two_theta_diff_plot = compute_results.two_theta_compare_figure(big_df)
        norm_int_plot = compute_results.create_norm_intensity_graph(big_df, ti_df, phase_df, current_two_theta, key)
        norm_int_plot.write_image(os.path.join(temp_path, key, 'norm_int_plot.pdf'))
        two_theta_diff_plot.write_image(os.path.join(temp_path, key, 'two_theta_diff.pdf'))

    if send_input:
        instprm_type, instprm_string = instprm_contents.split(',')

        decoded = base64.b64decode(instprm_string)
        f = open(temp_path + '/' + 'Input' + '/' + instprm_fname,'w')
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
            f = open(temp_path + '/' + 'Input' + '/' + fname,'w')
            to_write = decoded.decode('utf-8')
            to_write = re.sub('\\r','',to_write)
            f.write(to_write)
            f.close()
        
        for i in range(len(xrdml_contents)):
            contents = xrdml_contents[i]
            fname = xrdml_fnames[i]
            
            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            f = open(temp_path + '/' + 'Input' + '/' + fname,'w')
            to_write = decoded.decode('utf-8')
            to_write = re.sub('\\r','',to_write)
            f.write(to_write)
            f.close()

    #send directory to zip and return
    report_str = 'report' + str(hash)
    shutil.make_archive(report_str, 'zip', 'calculator_report' + str(hash))
    return send_file(report_str + '.zip')

@app.callback(
    Output('store-calculations', 'clear_data'),
    Input('page-listener', 'close')
)
def tab_close(close):
    if close == True:
        return True
    else:
        return None

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True,port=8050) 

@server.route("/AusteniteCalculator/app/")
def download():
    return flask.send_from_directory(root_dir, "austenitecalculator.pdf")

@server.route("/AusteniteCalculator/app/")
def download_report():
    return flask.send_from_directory(root_dir, "report.zip")

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