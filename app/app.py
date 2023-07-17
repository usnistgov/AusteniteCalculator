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
from plotly.tools import mpl_to_plotly

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
import math
from apscheduler.schedulers.background import BackgroundScheduler
import atmdata
from copy import deepcopy

# Add example comment

# user created
import compute_results
import compute_uncertainties
import interaction_vol

inside_docker = False

# Gsas
if platform.system() == 'Linux':
    sys.path.insert(0,'/root/g2full/GSASII/') # <- for Docker (assuming none of us use a Linux OS)
    inside_docker = True

# David's local development (add your own line to work on the project locally)
elif re.search('dtn1',os.getcwd()):
    sys.path.insert(0,'/Users/dtn1/Anaconda3/envs/gsas-AustCalc/GSASII/')

elif re.search('maxgarman',os.getcwd()):
    sys.path.insert(0,'/Users/maxgarman/opt/anaconda3/envs/gsas-AustCalc/GSASII/') 

elif re.search('creuzige',os.getcwd()):
    sys.path.insert(0, '/Users/creuzige/gsas2full/envs/gsas-AustCalc/GSASII/')

elif re.search('schen',os.getcwd()):
    sys.path.insert(0, '/Users/schen/.conda/envs/conda_gsas_env/GSASII/')

elif re.search('maxga', os.getcwd()):
    sys.path.insert(0, '/Users/maxga/anaconda3/envs/conda_gsas_env/GSASII/')


import GSASIIscriptable as G2sc
import GSASIIpath

try:
    GSASIIpath.svnUpdateDir(version=5300,verbose=True)
except Exception: #GSAS raises an execption if unable to connect to svn
    print("Unable to update, using whichever version is installed")


def clear_directory():
    dirs = glob.glob("calculator_report*/")
    for dir in dirs:
        shutil.rmtree(dir)
    zips = glob.glob("report*")
    for zip in zips:
        os.remove(zip)

# Clear the report directory every 24 hours
scheduler = BackgroundScheduler()
scheduler.add_job(clear_directory, 'interval', hours=24)
scheduler.start()

# Bottom banner and NIST formatting
custom_index = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <link rel="stylesheet" href="assets/nist-combined.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
        {%css%}
    </head>

    <body>
    <header class="nist-header" id="nist-header" role="banner">
    <a href="https://www.nist.gov/" title="National Institute of Standards and Technology" class="nist-header__logo-link" rel="home">
        <svg aria-hidden="true" class="nist-header__logo-icon" version="1.1" xmlns="http://www.w3.org/2000/svg" width="24" height="32" viewBox="0 0 24 32">
        <path d="M20.911 5.375l-9.482 9.482 9.482 9.482c0.446 0.446 0.446 1.161 0 1.607l-2.964 2.964c-0.446 0.446-1.161 0.446-1.607 0l-13.25-13.25c-0.446-0.446-0.446-1.161 0-1.607l13.25-13.25c0.446-0.446 1.161-0.446 1.607 0l2.964 2.964c0.446 0.446 0.446 1.161 0 1.607z"></path>
        </svg>
        <svg class="nist-header__logo-image" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="-237 385.7 109.7 29.3">
        <title>National Institute of Standards and Technology</title>
        <g>
            <path class="st0" d="M-231,415h-6v-23.1c0,0,0-4.4,4.4-5.8c4-1.3,6.6,1.3,6.6,1.3l19.7,21.3c1,0.6,1.4,0,1.4-0.6v-22h6.1V409
            c0,1.9-1.6,4.4-4,5.3c-2.4,0.9-4.9,0.9-7.9-1.7l-18.5-20c-0.5-0.5-1.8-0.6-1.8,0.4L-231,415L-231,415z"/>
            <path class="st0" d="M-195,386.1h6.1v20.7c0,2.2,1.9,2.2,3.6,2.2h26.8c1.1,0,2.4-1.3,2.4-2.7c0-1.4-1.3-2.8-2.5-2.8H-176
            c-3,0.1-9.2-2.7-9.2-8.5c0-7.1,5.9-8.8,8.6-9h49.4v6.1h-12.3V415h-6v-22.9h-30.2c-2.9-0.2-4.9,4.7-0.2,5.4h18.6
            c2.8,0,7.4,2.4,7.5,8.4c0,6.1-3.6,9-7.5,9H-185c-4.5,0-6.2-1.1-7.8-2.5c-1.5-1.5-1.7-2.3-2.2-5.3L-195,386.1
            C-194.9,386.1-195,386.1-195,386.1z"/>
        </g>
        </svg>
    </a>
    </header>
        
    {%app_entry%}
    {%config%}
    {%scripts%}
    {%renderer%}
      
        <footer class="nist-footer">
        
        <div class="nist-footer__inner">
            <div class="nist-footer__menu" role="navigation">
            <ul>
                <li class="nist-footer__menu-item">
                <a href="https://www.nist.gov/privacy-policy">Site Privacy</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.nist.gov/oism/accessibility">Accessibility</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.nist.gov/privacy">Privacy Program</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.nist.gov/oism/copyrights">Copyrights</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.commerce.gov/vulnerability-disclosure-policy">Vulnerability Disclosure</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.nist.gov/no-fear-act-policy">No Fear Act Policy</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.nist.gov/foia">FOIA</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.nist.gov/environmental-policy-statement">Environmental Policy</a>
                </li>
                <li class="nist-footer__menu-item ">
                <a href="https://www.nist.gov/summary-report-scientific-integrity">Scientific Integrity</a>
                </li>
                <li class="nist-footer__menu-item ">
                <a href="https://www.nist.gov/nist-information-quality-standards">Information Quality Standards</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.commerce.gov/">Commerce.gov</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.science.gov/">Science.gov</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://www.usa.gov/">USA.gov</a>
                </li>
                <li class="nist-footer__menu-item">
                <a href="https://vote.gov/">Vote.gov</a>
                </li>
            </ul>
            </div>
        </div>
        <div class="nist-footer__logo">
            <a href="https://www.nist.gov/" title="National Institute of Standards and Technology" class="nist-footer__logo-link" rel="home">
            <img src="assets/nist_logo_brand_white.svg" alt="National Institute of Standards and Technology logo" />
            </a>
        </div>
        </footer>

    </body>
</html>"""


app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.COSMO],
                index_string = custom_index)

server = app.server
root_dir = os.getcwd()


app.layout = dbc.Container([
      ### ---  Top Banner --- ###
    html.Br(),
    html.H1('Austenite Calculator'),
    html.Div(['Calculating ',
        html.Span("Austenite",
                  id="tooltip-target",
                  style={"textDecoration": "underline", "cursor": "pointer"},
                ),
      ' since 2021.'],style={'font-style':'italic'}),
    dbc.Tooltip(
            "Austenite, also known as gamma-phase iron (γ-Fe), is a metallic, non-magnetic allotrope of iron or a solid solution of iron with an alloying element.",
            target="tooltip-target",
    ),
    html.Br(),
    
    dbc.Tabs([

        ### --- start Data Upload tab --- ###

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
                            dbc.Button('X-Ray Diffraction File (.csv, .xrdml, etc.)')
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
            html.Br(),
            #json upload for crystallites illuminated
            dcc.Upload(
                    id='upload-json',
                    children=html.Div([
                            dbc.Button('Crystallites Illuminated JSON (.json) - see \'File Creation\' Tab')
                            ])),
            html.Div(id='f4-name'),

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

            ## Checkbox to use Example 08A files instead
            html.Hr(),
            dbc.Checklist(
                options=[
                    {"label": "Co Source Q&P (Example 08A Files)", "value": 1},
                ],
                id="example08A-files-check",
            ),

            #start of interaction volume inputs
            #atoms per cell-.cif file
            #f-prime and f-doubleprime-each element in .cif
            #

            # inference method
            html.Hr(),
            html.Div("Statistical Inference Option:"),
            dbc.RadioItems(
                options=[
                    {"label": "MCMC (slower, but most accurate)", "value": 1},
                    {"label": "Variational Inference (faster, but less accurate)", "value": 2}
                ],
                value=1,
                id="inference-method",
            ),
            html.Br(),
            html.Div("Number of MCMC Warmup Runs (only applicable if MCMC selected above)"),
            dbc.Row(
                dbc.Col(dbc.Select(
                            id="number-mcmc-runs",
                            options=[
                                {"label": "4000", "value":4000},
                                {"label": "8000", "value":8000},
                                {"label": "1000 (for testing only)", "value":1000},
                            ],
                            value=1000 #default value on screen
                        ), width=3)
            ),

            # submit button
            html.Hr(),
            html.Div("""Once your files have been uploaded, click the button below
                     to begin the analysis."""),
            html.Br(),
            dbc.Button(id='submit-button-state', n_clicks=0, children='Begin Analysis'), 
            html.Br(),
            html.Br(),
            # Download Button
            dbc.Button(id='report-button', children='Download Analysis Report'),
            Download(id='download-full-report'),
            html.Br(),
            dcc.Store(id='store-calculations', storage_type='memory'),
            html.Br(),
            # Loading icons/animation
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
            
        ### --- end Data Upload tab --- ###


        ### --- start Intensity Plots tab --- ###
        dbc.Tab([
            html.Br(),
            html.Div(id='intensity-plot-placeholder',children=[
                dcc.Dropdown(options = ['Dataset: 1'], 
                            id = 'intensity-plot-dropdown',
                            value='Dataset: 1')
             ]),
            html.Br(),
            html.Div("""Plot of the raw data, plotted as a continuous line.
                        Hovering a cursor over the plot will bring up a
                        menu to save, zoom, and other features."""),
            dcc.Graph(id='intensity-plot'),
            html.Br(),
            html.Div("""Plot of the raw data and fit. Raw data is plotted as
                        points, fitted data as lines. The fit value should nominally
                        overlap the raw data. Inspect the data to confirm."""),
            dcc.Graph(id='fitted-intensity-plot')
            ],
            label="Intensity Plots"),
        
        ### --- end Intensity Plots tab --- ###
        
        ### --- start Normalized Intensities Tab --- ###
        dbc.Tab([
            html.Br(),
            html.Div(id='fit-theo-table-placeholder',children=[
                dcc.Dropdown(options = ['Dataset: 1'], 
                            id = 'fit-theo-table-dropdown',
                            value='Dataset: 1')
             ]),
            html.Br(),
            

            html.Br(),
            html.Div("""Table of Fit and Theoretical Intensities"""),
            dash_table.DataTable(id='intensity-table'),
            html.Br(),
            html.Button("Download as CSV", id="intensity-table-button"),
            dcc.Download(id="intensity-table-download"),
            #
            html.Br(),
            html.Br(),
            html.Div(id='norm-int-plot-placeholder',children=[
                dcc.Dropdown(options = ['Dataset: 1'], 
                            id = 'norm-int-plot-dropdown',
                            value='Dataset: 1')
             ]),
            html.Br(),
            html.Div("""Plot of the Normalized Intensities.  The value for each phase should be constant.
                        Deviation from a constant value indicates unaccounted for factors in normalization,
                        such as texture, instrument calibration, and/or microstructure effects"""),
            dcc.Graph(id='normalized-intensity-plot'),
            html.Br(),
            html.Div(id='two-theta-diff-plot-placeholder',children=[
                dcc.Dropdown(options = ['Dataset: 1'], 
                            id = 'two-theta-diff-plot-dropdown',
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
            html.Br(),
            html.Hr(),
            html.Br()
            
            #Tab label
            ],
            label="Normalized intensities"),
            
            
            
        ### --- end Normalized Intensities Tab --- ###

        ### --- start Phase Fraction Tab --- ###

        dbc.Tab([
            html.Br(),
            html.Div(id='unit-placeholder',children=[ 
                'Select units for Phase Fraction',
                dcc.Dropdown(options = [{'label':'Number of Unit Cells', 'value':'Number of Unit Cells'}, 
                                        {'label':'Volume of Unit Cells', 'value':'Volume of Unit Cells'}, 
                                        {'label':'Mass of Unit Cells', 'value':'Mass of Unit Cells'}], 
                            value = 'Number of Unit Cells',
                            id = 'unit-dropdown')
             ]),
            html.Br(),
            html.H3("""Figure for Phase Fraction Uncertainty"""),
            html.Div("""The figure below displays probability distributions conveying the estimates and \n
                     uncertainty for the phase fractions. Tall and narrow distributions indicate more confidence \n
                     in the phase fraction, will wide and flat distributions indicate more uncertainty."""),
            dcc.Graph(id='pf-uncert-fig'),
            html.Br(),
            html.H3("""Table for Phase Fraction Uncertainty"""),
            html.Div("""The table below gives summary statistics of the above figure, including estimates of the \n
                     phase fractions as well as 95% credible intervals."""),
            html.Br(),
            dash_table.DataTable(id='pf-uncert-table'),
            html.Br(),
            html.Hr(),
            html.Br(),
            html.H3("Sources of Uncertainty"),
            html.Div("""The table below gives estimates for various sources of uncertainty, 
                     including the experimental error, sample-to-sample error (if multiple samples are uploaded), 
                     the median (across all peaks) of the X-ray count uncertainties, and the median (across all peaks) 
                     of the uncertainties for parameter fit. """),
            html.Br(),
            dash_table.DataTable(id='param-table'),
            html.Br(),
            html.Hr(),
            html.Br(),
            html.H3("Uncertainty Due to Fit and Count for Each Peak"),
            html.Div("""The following table gives uncertainties for counting and fitting statistics for all fitted peaks."""),
            html.Br(),
            dash_table.DataTable(id='u-int-fit-count-table',
                                 page_size=20,
                                 page_current=0,
                                 filter_action="native",
                                 sort_action="native",
                                 column_selectable="single"),
            html.Br(),
            html.Div("""Table of Phase Fractions"""),
            dash_table.DataTable(id='phase-frac-table'),
            html.Br(),
            html.Div("""Flagged Notes to Users"""),
            dash_table.DataTable(id='uncert-table'),
            html.Br(),
            
            #Tab label
            ],
            label="Phase Fraction"),

        ### --- end uncertainty analysis --- ###
        
        ### --- start Interaction Volume Tables and Plots --- ###
        
        dbc.Tab([
            html.Br(),
            html.Div("Select dataset:"),
            html.Div(id='interaction-vol-plot-placeholder',children=[
                    dcc.Dropdown(options = ['Dataset: 1'],
                                id = 'interaction-vol-plot-dropdown',
                                value='Dataset: 1')]),

            html.Br(),
            html.Div("Select phase:"),
            html.Div(id='interaction-vol-plot-phase-placeholder',children=[
                    dcc.Dropdown(options = ['Phase: 1'], 
                                id = 'interaction-vol-plot-phase-dropdown',
                                value='Phase: 1')]),
            html.Br(),
            html.Div("Select peak:"),
            html.Div(id='peak-placeholder',children=[
                    dcc.Dropdown(options = ['1'],
                                id = 'peak-dropdown',
                                value='1')]),
            html.Br(),
            dash_table.DataTable(id='crystallites-table'),
            html.Br(),
            html.Div([
                dcc.Graph(id='centroid-plot'),
                dcc.Graph(id='interaction-depth-plot'),
            ]),

        ],
        label='Interaction Volume'),
        
        ### --- end Interaction Volume Tables and Plots --- ###

        

        ### --- start File Creation --- ###
        ## Section to create .instprm file
        dbc.Tab([
            html.Div([
                'Please choose from a default .instprm file if you do not have one, upload your .cif and .xrdml files, and click the \'Download .instprm File\' Button',
                dcc.Dropdown(id='default-dropdown',options=['CuKa', 'APS 30keV 11BM', '0.7A synchrotron', '1.9A ILL D1A CW', '9m HIPD 151 deg bank TOF', '10m TOF 90deg bank']),
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
            html.Div([html.Button("Download .instprm File", id = "download-created-file"), Download(id = "download-instprm")]),
            html.Br(),
            ## Section to create .json file
            html.Div([
                '***WIP*** To create a .json file for the crystallites illuminated calculation, please fill the following fields and click the \'Download .json File\' Button',
                #need fields for:
                
                #beam shape and size
                dcc.Dropdown(
                    id = 'beam-shape-in',
                    options = ['Circle', 'Square']
                ),
                dcc.Input(
                    id = 'beam-size-in',
                    type = 'number',
                    placeholder = 'beam size(mm)'
                ),
                #raster in x and y
                dcc.Input(
                    id = 'raster-x-in',
                    type = 'number',
                    placeholder = 'raster length x(mm)'
                ),
                dcc.Input(
                    id = 'raster-y-in',
                    type = 'number',
                    placeholder = 'raster length y(mm)'
                ),
                #L, W_F, H_F, H_R?? - make inputs for these and then have Adam write a description
                dcc.Input(
                    id = 'L-in',
                    type = 'number',
                    placeholder = 'L(mm)'
                ),

                dcc.Input(
                    id = 'W-F-in',
                    type = 'number',
                    placeholder = 'W_F'
                ),

                dcc.Input(
                    id = 'H-F-in',
                    type = 'number',
                    placeholder = 'H_F'
                ),

                dcc.Input(
                    id = 'H-R-in',
                    type = 'number',
                    placeholder = 'H_R'
                ),
                html.Br(),
                html.Br(),
                html.Div(
                    [dbc.Button("Download .json File", id = "download-created-json"),
                    Download(id = "download-json")]),
            ]),
        ],
        label="File Creation"),
        ### --- end Instrument Parameter Creation --- ###

        ### --- start About Tab --- ###

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
        ### --- end About Tab --- ###

    ], # end dbc.Tabs()
    id="tabs")
    
])

### --- file upload messages --- ###
# Pairs of app.callback and trailing function definitions
# Text should appear under the button

### --- data upload tab --- ###

### --- X-Ray Diffraciton File --- ###
@app.callback(
    Output('f1-name','children'),
    Input('upload-data-xrdml','filename')
)
def show_f1_name(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded Files: " + ', '.join(filename)

### --- Instrument Parameter File --- ###
@app.callback(
    Output('f2-name','children'),
    Input('upload-data-instprm','filename')
)
def show_f2_name(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded File: " + filename


### --- Crystallographic Information Files --- ###
@app.callback(
    Output('f3-name','children'),
    Input('upload-cif','filename')
)
def show_f3_name(filename):
    
    if filename is None:
        return ""
        
    else:
        print(filename)
        return "Uploaded Files: " + ', '.join(filename)
        
### --- Crystallites Illuminated JSON --- ###
@app.callback(
    Output('f4-name','children'),
    Input('upload-json','filename')
)
def show_f4_name(filename):
    
    if filename is None:
        return ""
        
    else:
        print(filename)
        return "Uploaded File: " + filename

### --- File Creation tab --- ###
### --- Choose default .instprm --- ###
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

### --- Choose calibration .cif --- ###
@app.callback(
    Output('default-cif','children'),
    Input('upload-default-cif','filename')
)
def show_cif_names(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded Files: " + ', '.join(filename)

### --- Choose calibration Xray File --- ###
@app.callback(
    Output('default-xrdml','children'),
    Input('upload-default-xrdml','filename')
)
def show_xrdml_name(filename):
    
    if filename is None:
        return ""
        
    else:
        return "Uploaded Files: " + ', '.join(filename)

### --- Download Created .instprm File --- ###

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

# json upload dialog - moved to front panel

# ADD DOWNLOAD .JSON

#    State('upload-json','contents'),
#    State('upload-json','filename'),

#@app.callback(
#    Output('default-json','children'),
#    Input('upload-json','filename')
#)
#def show_json_name(filename):
#
#    if filename is None:
#        return ""
#
#    else:
#        return "Uploaded Files: " + ', '.join(filename)


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
    Output('intensity-plot-placeholder', 'children'),
    Output('fit-theo-table-placeholder', 'children'),
    Output('two-theta-diff-plot-placeholder', 'children'),
    Output('interaction-vol-plot-phase-placeholder', 'children'),
    Output('norm-int-plot-placeholder', 'children'),
    Output('interaction-vol-plot-placeholder', 'children'),
    Output('store-calculations', 'data'),
    Output('submit-confirmation','children'),
    Output('u-int-fit-count-table','data'),
    Output('u-int-fit-count-table','columns'),
    Input('submit-button-state', 'n_clicks'),
    State('upload-data-xrdml','contents'),
    State('upload-data-xrdml','filename'),
    State('upload-data-instprm','contents'),
    State('upload-data-instprm','filename'),
    State('upload-cif','contents'),
    State('upload-cif','filename'),
    State('upload-json','contents'),
    State('upload-json','filename'),
    State('default-files-check','value'),
    State('example05-files-check','value'),
    State('example06-files-check','value'),
    State('example08A-files-check','value'),
    State('inference-method','value'),
    State('number-mcmc-runs','value'),
    prevent_initial_call = True
)
def update_output(n_clicks,
                  xrdml_contents,xrdml_fnames,
                  instprm_contents,instprm_fname,
                  cif_contents,cif_fnames,
                  csv_contents, json_fname,
                  use_default_files, use_example05_files, use_example06_files,
                  use_example08A_files,
                  inference_method_value,
                  number_mcmc_runs):
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
       use_example08A_files: checkbox to use example data 8A
       inference_method_value: selection for statistical inference method

    Returns:
        intensity_plot_dropdown: dropdown created for the raw and fit data graphs
        fit_theo_table_dropdown: dropdown created for the norm_int table and phase_frac table
        two_theta_diff_plot_dropdown: dropdown created for the difference in theo_int graph and phase_frac variation graph
        norm_int_plot_dropdown: dropdown for the variation in normalized intensity graph
        main_dict: dictionary created to store data from compute_results
        conf: return to show that app is done loading

    Raises:
       
    '''
    
    # point towards directory and upload data using GSASII
    # Default data location
    print(use_default_files)

    if use_default_files not in [None, []] and use_default_files[0] == 1:
        #datadir = '../server_default_datadir'
        datadir = '../ExampleData/Example01'
        cif_fnames = ['austenite-Duplex.cif','ferrite-Duplex.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper_power.xrdml']
        instprm_fname = 'TestCalibration.instprm'
        json_fname = 'Example01.json'
        f = open(datadir + '/' + json_fname)
        json_data = f.read()
        json_string = json.loads(json_data)
        f.close()
        
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
        json_fname = 'Example05.json'
        
        
        
        #f = open(datadir + '/' + json_fname)
        with open(os.path.join(datadir, json_fname), 'r') as f:
            json_data = json.loads(f.read())
        f.close()
        
        print("Json path: ",f)
        print(json_data)
        #json_data = f.read()
        #json_string = json.loads(json_data)
        #print(json_string)



    elif use_example06_files not in [None, []] and use_example06_files[0] == 1:
        datadir = '../ExampleData/Example06'
        #datadir = '../ExampleData/Example01'
        cif_fnames = ['alpha-prime-martensite-SRI.cif','epsilon-martensite-SRI.cif','austenite-SRI.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['Example06_simulation_generation_data.csv']
        instprm_fname = 'BrukerD8_E211110.instprm'
        json_fname = 'Example06.json'
        f = open(datadir + '/' + json_fname)
        json_data = f.read()
        json_string = json.loads(json_data)
        f.close()

    elif use_example08A_files not in [None, []] and use_example08A_files[0] == 1:
        datadir = '../ExampleData/Example08A'
        #datadir = '../ExampleData/Example01'
        cif_fnames = ['austenite-FeOnly.cif','ferrite-FeOnly.cif']
        workdir = '../server_workdir'
        xrdml_fnames = ['QP980_AR_th-tthscan_AR0p5_trunc.csv']
        instprm_fname = 'ThomasXRD-Co-Cal.instprm'
        json_fname = 'QP_A.json'
        f = open(datadir + '/' + json_fname)
        json_data = f.read()
        json_string = json.loads(json_data)
        f.close()


    #Stores user files in a directory
    else:
        datadir = '../server_datadir'
        workdir = '../server_workdir'

        # For each uploaded file, save (on the server)
        # ensuring that the format matches what GSAS expects.

        # first, read instrument parameter file

        instprm_type, instprm_string = instprm_contents.split(',')

        decoded = base64.b64decode(instprm_string)
        f = open(datadir + '/' + instprm_fname,'w')
        to_write = decoded.decode('utf-8')
        if re.search('(instprm$)',instprm_fname) is not None:
            to_write = re.sub('\\r','',to_write)
        f.write(to_write)
        f.close()


        ####FIX
        # Is this for the export data as csv, or illuminated json file?
        # AC 7 June 2023 - I think this is for the json file but what?
        csv_type, csv_string = csv_contents.split(',')

        decoded = base64.b64decode(csv_string)
        f = open(datadir + '/' + json_fname,'w')
        to_write = decoded.decode('utf-8')
        csv_string = to_write
        if re.search('(csv$)',json_fname) is not None:
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

    ### Read in JSON File
    # Needed earlier for some of the theoretical intensity data
    # AC 2023 June 07 - why here?
    
    with open(os.path.join(datadir, json_fname), 'r') as f:
        crystal_data = json.loads(f.read())
    f.close()
    #crystal_data = json.loads(json_string)
    
    #need to convert strings to numbers in json dict
    
    # May need to adjust for multi array
    #AC - Why use strings? Try without
#        for key in crystal_data.keys():
#            if(key != 'beam_shape'):
#                if(crystal_data[key][0] == '['):
#                    crystal_data[key] = crystal_data[key].strip('][').split(',')
#                    for x in range(len(crystal_data[key])):
#                        crystal_data[key][x] = float(crystal_data[key][x])
#                else:
#                    crystal_data[key] = float(crystal_data[key])
#



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
        print("Compute results for file ",x)
        fit_data, results_df, phase_frac_DF, two_theta, tis, uncert_DF = compute_results.compute(datadir,workdir,xrdml_fnames[x], \
                                    instprm_fname,cif_fnames,crystal_data, G2sc)
        temp_string = 'Dataset: ' + str(x + 1)
        results_df['sample_index'] = str(x + 1)
        
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
        print("Finish results for file ",x)

    # full results table
    full_results_table = pd.concat(results_table,axis=0,ignore_index=True)
    full_results_table = full_results_table.loc[full_results_table['Peak_Fit_Success'],:]
    full_results_table['Uncertainties due to Fitting'] = full_results_table['u_int_fit']/full_results_table['R_calc']
    full_results_table['Uncertainties due to Counts'] = full_results_table['u_int_count']/full_results_table['R_calc']
    full_results_table = full_results_table.loc[:,['sample_index','Phase','Uncertainties due to Counts','Uncertainties due to Fitting']]
    u_int_fit_count_table_data, u_int_fit_count_table_columns = compute_results.df_to_dict(full_results_table.round(6))
    
    #have the option to run the interaction volume calcs for each dataset(assume they are the "same data"), default is no
    print("Begin Interaction Volume")
    scattering_dict = {}
    atomic_masses = {}
    elem_fractions = {}
    cell_volumes = {}
    cell_masses = {}
    for x in range(len(cif_fnames)):
#        print("Compute results for cif file ",x)
        print("Compute results for cif file ",cif_fnames[x])
        cif_path = os.path.join(datadir, cif_fnames[x])
        instprm_path = os.path.join(datadir, instprm_fname)
        
        addon = False
        elems = []
        crystal_density = None
        print("Begin Open files")
        # Somewhat fragile to cif format and number of returns after line ending
        with open(cif_path) as f:
            lines = f.readlines()
            for line in lines:
                if len(line.split()) > 0:
                    if line.split()[0] == '_cell_volume':
                        cell_volumes[cif_fnames[x]] = (float(line.split()[1].split('(')[0]))
                    if line.split()[0] == '_exptl_crystal_density_diffrn':
                        crystal_density = float(line.split()[1])
                if addon == True and len(line) > 1:
                    elems.append(line)
                if addon == True and len(line) <= 1:
                    addon = False
                #changed to string comparison as the syntax changed some
                if 'symmetry_multiplicity' in line:
                    addon = True
        
        print("Begin parameter files readin")
        wavelengths = []
        with open(instprm_path) as fi:
            lines = fi.readlines()
            for line in lines:
                if line != '#GSAS-II instrument parameter file; do not add/delete items!':
                    line_split = line.split(':')
                    if line_split[0] == 'Lam1' or line_split[0] == 'Lam2' or line_split[0] == 'Lam':
                        wavelengths.append(float(line_split[1].strip('\n')))
        
        print("Element Calculation")
        elems_for_phase = []
        elem_percentage = []
        atoms_per_cell = None
        
        # Should throw an error message if the list is blank...
        for elem in elems:
            print("running element ", elem)
            temp = elem.split()
            elems_for_phase.append(temp[1])
            elem_percentage.append(float(temp[5]))
            atoms_per_cell = int(temp[8])
            #print("Results: ", elems_for_phase, elem_percentage,atoms_per_cell)
        
        print("Cell Volume Calculation")
        cell_mass = 0.0
        count = 0
        for elem in elems_for_phase:
            key = elem + '_'
            elem_mass = atmdata.AtmBlens[key]['Mass']
            # included the atoms per cell here
            cell_mass += elem_mass * elem_percentage[count] * atoms_per_cell
            atomic_masses[elem] = elem_mass
            print("Element: ", elem,"\tMass: ",elem_mass)
            count += 1
        
        cell_masses[cif_fnames[x]] = cell_mass
        print(cell_mass, ' ', cell_masses)

        print("Begin Cell Density")
        cell_density = cell_mass/cell_volumes[cif_fnames[x]]
        pack_fraction = crystal_density/cell_density
        #print(cell_density,pack_fraction)
        elem_details = interaction_vol.getFormFactors(elems_for_phase)
        #print(elem_details)
        scattering_nums = []
        for elem in elem_details:
            #print(elem)
            scattering_nums.append(interaction_vol.findMu(elem, wavelengths, pack_fraction, cell_volumes[cif_fnames[x]])) #scattering nums has elem_sym, f', f'', and mu
            #print(elem, scattering_nums)
        
        print("Begin Cell Scattering")
        for elem in scattering_nums:
            elem[1] = elem[1][0]
            elem[2] = elem[2][0]
            elem.append(atoms_per_cell)

        scattering_dict[cif_fnames[x]] = scattering_nums
        elem_fractions[cif_fnames[x]] = elem_percentage
        
    print("End Interaction Volume")
    
    peaks_dict = {}
    for phase_name in cif_fnames:
        peaks_dict[phase_name] = []
        
    print("Begin Results Table")
    # Peak dictionary includes F value, multiplicity, theta position, F_squared value
    # doesn't seem like the values are quite right... AC 3 Mar 2023
    for row in results_table['Dataset: 1'].iterrows():
        current_peak = []
        current_peak.append(math.sqrt(row[1]['F_calc_sq'])/scattering_dict[row[1]['Phase']][0][4])
        current_peak.append(row[1]['mul'])
        current_peak.append(row[1]['pos_fit']/2)
        final_FF = 0.0
        for elem in scattering_dict[row[1]['Phase']]:
            count = 0
            FF=(elem[4]*(current_peak[0]+elem[1]))**2+(elem[4]*elem[2])**2
            final_FF += FF * elem_fractions[row[1]['Phase']][count]
            count += 1
        current_peak.append(final_FF)
        peaks_dict[row[1]['Phase']].append(current_peak)

    print("Before Summarized Phase Info")

    summarized_phase_info = {}
    for key, value in scattering_dict.items():
        summarized_phase_info[key] = [0.0,0.0, 0.0]
        current_fracs = elem_fractions[key]
        for i in range(len(value)):
            summarized_phase_info[key][0] += (value[i][1] * current_fracs[i])
            summarized_phase_info[key][1] += (value[i][2] * current_fracs[i])
            summarized_phase_info[key][2] += (value[i][3] * current_fracs[i])
    
    graph_data_dict = {}
    for key, value in peaks_dict.items():
        current_summarized_data = summarized_phase_info[key]
        graph_data_dict[key] = []
        for peak in value:
            data_list = interaction_vol.create_graph_data(peak, current_summarized_data)
            graph_data_dict[key].append(data_list)
        #create a dict with keys as phases, nested list with each inner list being that peaks f_elem, mul, and theta
    
    ####################################################
    #beginning of crystallites illuminated calculations
    ####################################################
    
    crystallites_dict = {}
    #run calculations for each peak of each phase, crystallites dict has keys for phases and values are [[]] with each inner list as a peak in that phase
    
    # add a try/except here to confirm the filenames match
    
    print("Peaks dictionary")
    print(peaks_dict)
    
    # Same dataset ok since the material is nominally the same?
    for cif_name, peak_data in peaks_dict.items():
        print("Phase: ", cif_name)
        for x in range(len(peak_data)):
            
            # this calculation is redundant, so we can potentially move outside the loop, but overhead is minimal in the meantime
            crystal_data = compute_results.format_crystal_data(crystal_data,cif_name) # <- adam may fix the formatting on the json files to make this not necessary

            num_layer, num_ill, frac_difrac, num_difrac = interaction_vol.crystallites_illuminated_calc(crystal_data,
                phase_frac['Dataset: 1'].loc[phase_frac['Dataset: 1']['Phase'] == cif_name, 'Phase_Fraction'].values[0],
                crystal_data[cif_name][0],
                crystal_data[cif_name][1],
                peak_data[x][1],
                peak_data[x][2],
                crystal_data[cif_name][2])
            if cif_name in crystallites_dict.keys():
                crystallites_dict[cif_name].append([num_layer, num_ill, frac_difrac, num_difrac])
            else:
                crystallites_dict[cif_name] = []
                crystallites_dict[cif_name].append([num_layer, num_ill, frac_difrac, num_difrac])
    # run MCMC using full results
    print("Before Inference Method")
    
    if inference_method_value == 1:
        fit_vi = False
    
    else:
        fit_vi = True

    results_table_df = pd.concat(results_table,axis=0).reset_index()
    mcmc_df = compute_uncertainties.run_stan(results_table,int(number_mcmc_runs),fit_vi)
    unique_phases = np.unique(results_table_df.Phase)
    param_table = compute_uncertainties.generate_param_table(mcmc_df,unique_phases,results_table_df)

    mcmc_df.drop(inplace=True,columns=mcmc_df.columns[mcmc_df.columns.str.contains('sigma')])
    print("{} mcmc samples obtained.".format(mcmc_df.shape[0]))
    print(mcmc_df.info(memory_usage=True))

    print("After Inference Method")

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
    
    for key, value in graph_data_dict.items():
        for peak in value:
            endpoints_dict, endpoints_cols = compute_results.df_to_dict(peak[0].round(3))
            mids_dict, mids_cols = compute_results.df_to_dict(peak[1].round(3))
            peak[0] = (endpoints_dict, endpoints_cols)
            peak[1] = (mids_dict, mids_cols)

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
        

    # calculate alternate phase fraction units
    # pandas doesn't copy well
    mass_conversion = phase_frac.copy()
    volume_conversion = phase_frac.copy()
    
    #this needs to work for more than 2 phases, change to for loop
    #find denominator first(normalize at the same time)
    mass_denominator=0
    volume_denominator=0
    for dataset in mass_conversion:
        for x in range(len(mass_conversion[dataset][0])):
            mass_denominator += mass_conversion[dataset][0][x]['Phase_Fraction'] * cell_masses[mass_conversion[dataset][0][x]['Phase']]
            volume_denominator += (volume_conversion[dataset][0][x]['Phase_Fraction'] * cell_volumes[volume_conversion[dataset][0][x]['Phase']])

    # deepcopy to prevent aliasing
    mass_conversion = deepcopy(phase_frac)
    volume_conversion = deepcopy(phase_frac)
    
    #find denominator first(normalize at the same time)
    n_phases = len(phase_frac["Dataset: 1"][0])

    cell_mass_vecs = {}
    cell_volume_vecs = {}
    cell_number_vecs = {}

    for dataset in phase_frac:

        cell_mass_vecs[dataset] = np.zeros(n_phases)
        cell_volume_vecs[dataset] = np.zeros(n_phases)
        cell_number_vecs[dataset] = np.zeros(n_phases)

        for ii in range(n_phases):
            cell_mass_vecs[dataset][ii] = cell_masses[phase_frac[dataset][0][ii]['Phase']]
            cell_volume_vecs[dataset][ii] = cell_volumes[phase_frac[dataset][0][ii]['Phase']]
            cell_number_vecs[dataset][ii] = phase_frac[dataset][0][ii]['Phase_Fraction']

            # To get the number of atoms, open the phases data, 'Atoms' key
            # Any row (so [0]) should be fine, and then column [8]
            # print(phases["austenite-SRM487.cif"].data['Atoms'][0][8])

        for ii in range(n_phases):
            mass_conversion[dataset][0][ii]['Phase_Fraction'] = cell_number_vecs[dataset][ii]*cell_mass_vecs[dataset][ii]/np.sum(cell_number_vecs[dataset]*cell_mass_vecs[dataset])
            volume_conversion[dataset][0][ii]['Phase_Fraction'] = cell_number_vecs[dataset][ii]*cell_volume_vecs[dataset][ii]/np.sum(cell_number_vecs[dataset]*cell_volume_vecs[dataset])
    mass_conversion, volume_conversion, cell_mass_vec, cell_volume_vec = compute_results.get_conversions(phase_frac,cell_masses,cell_volumes)

    main_dict = {
        'results_table':results_table,
        'phase_frac':phase_frac,
        'volume_conversion':volume_conversion,
        'mass_conversion':mass_conversion,
        'two_thetas':two_thetas,
        'ti_tables':ti_tables,
        'uncert':uncert,
        'altered_results':altered_results,
        'altered_phase':altered_phase,
        'altered_ti':altered_ti,
        'fit_points':fit_points,
        'interaction_vol_data':graph_data_dict,
        'cell_masses':cell_masses,
        'cell_volumes':cell_volumes,
        'cell_mass_vec':cell_mass_vec.tolist(),
        'cell_volume_vec':cell_volume_vec.tolist(),
        'mu_samps':mcmc_df.to_dict(orient='list'), # inverse operation to pd.DataFrame({'col1':[1,2,3],'col2':[2,3,4], etc})
        'param_table':param_table.to_dict(orient='list'),
        'crystallites':crystallites_dict
    }
    
    #create html components to replace the placeholders in the app
    #ORDER NEEDS TO MATCH ABOVE
    
    intensity_plot_dropdown = html.Div([
        'Please select a dataset to view the intensity plot',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))] + ['View all datasets'], 
                    id = 'intensity-plot-dropdown',
                    value = 'Dataset: 1')
    ])

    norm_int_plot_dropdown = html.Div([
        'Please select a dataset to view the normailzed intensities plot',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))] + ['View all datasets'], 
                     id = 'norm-int-plot-dropdown',
                     value='Dataset: 1')
    ])

    interaction_vol_plot_dropdown = html.Div([
        'Please select a dataset to view the interaction volume',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))], 
                     id = 'interaction-vol-plot-dropdown',
                     value='Dataset: 1')
    ])

    fit_theo_table_dropdown = html.Div([
        'Please select a dataset to view the fit and theoretical intensities table',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))], 
                     id = 'fit-theo-table-dropdown',
                     value='Dataset: 1')
    ])

    two_theta_diff_plot_dropdown = html.Div([
        'Please select a dataset to view the difference between fit and theoretical two theta values',
        dcc.Dropdown(options = ['Dataset: ' + str(i + 1) for i in range(len(xrdml_fnames))], 
                     id = 'two-theta-diff-plot-dropdown',
                     value='Dataset: 1')
    ])

    interaction_vol_plot_phase_dropdown = html.Div([
        'Please select a phase to view the interaction volume',
        dcc.Dropdown(options = [phase for phase in cif_fnames], 
                     id = 'interaction-vol-plot-phase-dropdown',
                     value=' ')
    ])

    print("Submission complete. Navigate the above tabs to view results.")
    conf = "Submission complete. Navigate the above tabs to view results."

    #breakpoint()

    return (intensity_plot_dropdown,
            fit_theo_table_dropdown,
            two_theta_diff_plot_dropdown,
            interaction_vol_plot_phase_dropdown,
            norm_int_plot_dropdown,
            interaction_vol_plot_dropdown,
            main_dict,
            conf,
            u_int_fit_count_table_data,
            u_int_fit_count_table_columns)


@app.callback(
    Output('pf-uncert-fig','figure'),
    Output('pf-uncert-table','data'),
    Output('pf-uncert-table','columns'),
    Output('param-table','data'),
    Output('param-table','columns'),
    Input('store-calculations','data'),
    Input('unit-dropdown','value'),
    prevent_initial_call=True
)
def update_phase_fraction_plt_and_tbl(data,unit_value):
    """

    Creates Phase Fraction distribution plot and table with variable units
    Parameters and Returns come from preceeding @app.callback statement
    
    Parameters:
        data: data saved in dcc.Store from running compute_results
        unit_value: drop down menu for phase fraction unit
    
    Returns:
        | the following items
        | **pf_uncert_fig** plot "Figure for Phase Fraction Uncertainty"
            on tab "Phase Fraction"
        | **pf_uncert_data** data used in "Table for Phase Fraction Uncertainty"
            on tab "Phase Fraction"
        | **pf_uncert_cols** column names used in "Table for Phase Fraction
            Uncertainty" on tab "Phase Fraction"


    """

    if data is None:
        return go.Figure(), [], []

    # phase fraction figure
    mu_samps = pd.DataFrame(data.get('mu_samps'))
    m_vec = np.array(data.get('cell_mass_vec'))
    v_vec = np.array(data.get('cell_volume_vec'))

    print(m_vec)
    print(v_vec)

    param_table = pd.DataFrame(data.get('param_table'))
    ncol = param_table.shape[1]

    if unit_value == 'Number of Unit Cells':
        pass

    elif unit_value == 'Volume of Unit Cells':
        mu_samps = compute_results.convert_mu_samps(mu_samps,v_vec)
        param_table.iloc[:,1:3] = param_table.iloc[:,1:(ncol+1)].apply(lambda x: x*v_vec/sum(v_vec),axis=0)

    elif(unit_value == 'Mass of Unit Cells'):
        mu_samps = compute_results.convert_mu_samps(mu_samps,m_vec)
        param_table.iloc[:,1:3] = param_table.iloc[:,1:(ncol + 1)].apply(lambda x: x*m_vec/sum(m_vec),axis=0)

    table = data.get('results_table')
    results_table = compute_uncertainties.concat_results_tables(table,from_records=True)
    pf_uncert_fig = compute_uncertainties.generate_pf_plot(mu_samps,np.unique(results_table.Phase))

    pf_table = compute_uncertainties.generate_pf_table(mcmc_df=mu_samps,unique_phase_names=np.unique(results_table.Phase))
    pf_uncert_data, pf_uncert_cols = compute_results.df_to_dict(pf_table)

    param_table_data, param_table_columns = compute_results.df_to_dict(param_table.round(5))

    return pf_uncert_fig, pf_uncert_data, pf_uncert_cols, param_table_data, param_table_columns



@app.callback(
    Output('intensity-plot', 'figure'),
    Output('fitted-intensity-plot', 'figure'),
    Input('store-calculations', 'data'),  ## AC 3 Mar 2023- I don't see where this is
    Input('intensity-plot-dropdown', 'value'),
    prevent_initial_call = True
)
def update_intensity_plots(data, dataset_value):
    '''
    Args:
        data: data saved in dcc.Store from running compute_results
        dataset_value: dataset selected from dropdown

    Returns:
        raw_fig: raw data figure dynamically created in callback
        fig_fit_hist: fit data figure dynamically created in callback

    Raises:
        
    '''
    # Create empty plot if no data is provided
    if data is None:
        return go.Figure(), go.Figure()

    # Otherwise collect the data and extract it for plotting
    fit_data = data.get('fit_points').get(dataset_value)
    current_two_theta = data.get('two_thetas').get(dataset_value)
    
    # Option 1: to view all datasets
    if dataset_value == 'View all datasets':
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
        
    #Option 2: select a specific dataset from the dropdown
    else:
        fit_data = data.get('fit_points').get(dataset_value)
        current_two_theta = data.get('two_thetas').get(dataset_value)

        df = pd.DataFrame({
            "two_theta":current_two_theta,
            "intensity":fit_data[0]
        })
        
        # Plot of the raw data as a line profile
        raw_fig = px.line(df,x='two_theta',y='intensity')
        
        # Plot of the fitted data as a line, raw data as points
        fig_fit_hist = compute_results.create_fit_fig(current_two_theta, fit_data, dataset_value)

        return raw_fig, fig_fit_hist

@app.callback(
    Output('intensity-table','data'),
    Output('intensity-table','columns'),
    Output('phase-frac-table','data'),
    Output('phase-frac-table','columns'),
    Output('uncert-table','data'),
    Output('uncert-table','columns'),
    Input('store-calculations', 'data'),
    Input('fit-theo-table-dropdown', 'value'),
    Input('unit-dropdown', 'value'),
    prevent_initial_call = True
)
def update_tables(data, value, unit_value):

    if data is None:
        return [], [], [], [], [], [], [], []

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
    uncert_table = data.get('uncert').get(value)[0]
    uncert_cols = data.get('uncert').get(value)[1]

    frac_table = None
    frac_cols = None

    if(unit_value == 'Number of Unit Cells'):
        frac_table = data.get('phase_frac').get(value)[0]
        frac_cols = data.get('phase_frac').get(value)[1]
    elif(unit_value == 'Volume of Unit Cells'):
        frac_table = data.get('volume_conversion').get(value)[0]
        frac_cols = data.get('volume_conversion').get(value)[1]
    elif(unit_value == 'Mass of Unit Cells'):
        frac_table = data.get('mass_conversion').get(value)[0]
        frac_cols = data.get('mass_conversion').get(value)[1]

    return table, cols, frac_table, frac_cols, uncert_table, uncert_cols



@app.callback(
    Output('two_theta-plot','figure'),
    Input('store-calculations', 'data'),
    Input('two-theta-diff-plot-dropdown', 'value'),
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
    Input('norm-int-plot-dropdown', 'value'),
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
    Output('peak-placeholder', 'children'),
    Input('store-calculations', 'data'),
    Input('interaction-vol-plot-phase-dropdown', 'value'),
    prevent_initial_call = True
)
def update_peak_dropdown(data, value):
    '''
    Args:
        data: data saved in dcc.Store from running compute_results
        value: phase selected from dropdown

    Returns:
        peak_dropdown: the dropdown component to select each peak in the phase selected
    Raises:
        
    '''
    if (data is None) or (data.get('interaction_vol_data').get(value) is None):

        peak_dropdown = html.Div([
            'Please select a peak to view',
             dcc.Dropdown(options = ['1'], 
                          id = 'peak-dropdown',
                          value='1')
        ])

        return peak_dropdown

    peaks = data.get('interaction_vol_data').get(value)


    peak_dropdown = html.Div([
        'Please select a peak to view',
        dcc.Dropdown(options = [str(i+1) for i in range(len(peaks))],
                     id = 'peak-dropdown',
                     value='1')
    ])

    return peak_dropdown

@app.callback(
    Output('centroid-plot', 'figure'),
    Output('interaction-depth-plot', 'figure'),
    Output('crystallites-table', 'data'),
    Output('crystallites-table', 'columns'),
    Input('store-calculations', 'data'),
    Input('interaction-vol-plot-dropdown', 'value'),
    Input('interaction-vol-plot-phase-dropdown', 'value'),
    Input('peak-dropdown', 'value'),
    prevent_initial_call = True
)
def update_interaction_vol_plot(data, dataset_value, phase_value, peak_value):
    '''
    Args:
        data: data saved in dcc.Store from running compute_results
        phase_value: phase selected from dropdown
        peak_value: peak selected of current phase

    Returns:
        | the following items
        | **centroid_plot** plot ""
            on tab "Interaction Volume"  Plot of x-ray centroid into material
        | **depth_plot** plot ""
            on tab "Interaction Volume"
        | **cryst_illuminated_data** data used in "" on tab "Interaction Volume"
        | **cryst_illuminated_cols** column names used in "" on tab "Interaction Volume"

    Raises:
        
    '''
    #return go.Figure(), go.Figure()
    
    #print("Interaction Volume Plot Update")
    #print("Passed Parameters: ", dataset_value, phase_value, peak_value)
    
    #need to pick dataset
    
    if (data is not None) and (data.get('interaction_vol_data').get(phase_value) is not None):
        #print("In if loop")
        current_peak = data.get('interaction_vol_data').get(phase_value)[int(peak_value) - 1]
        df_endpoint = pd.DataFrame.from_dict(current_peak[0][0])
        df_midpoint = pd.DataFrame.from_dict(current_peak[1][0])

        #print(df_endpoint, df_midpoint)
        
        
        
        #ADD Particle size not hardcode 40
        centroid_plot = interaction_vol.create_centroid_plot(df_midpoint, current_peak[3])
        depth_plot = interaction_vol.create_depth_plot(df_endpoint['x'], df_endpoint['y'], current_peak[4])
        #breakpoint()
        crystal_info = data.get('crystallites').get(phase_value)[int(peak_value)]
        # check the order
        placeholder_dict = {
            'Number of Layers': [crystal_info[0]],
            'Number Illuminated': [crystal_info[1]],
            'Diffracting Fraction': [crystal_info[2]],
            'Number Diffracting': [crystal_info[3]],
            'Centroid of Z depth': current_peak[3]
        }
        #return go.Figure(), depth_plot
        
        
        # I don't know why making this into a dataframe works better...
        placeholder_df=pd.DataFrame.from_dict(placeholder_dict)
        cryst_illuminated_data, cryst_illuminated_cols=compute_results.df_to_dict(placeholder_df)
        #breakpoint()

        return centroid_plot, depth_plot, cryst_illuminated_data, cryst_illuminated_cols
        #return go.Figure(), go.Figure(), cryst_illuminated_data, cryst_illuminated_cols
    else:
        #print("Returning empty plot")
        return go.Figure(), go.Figure(), [], []

@app.callback(
    Output('download-json', 'data'),
    Input('download-created-json', 'n_clicks'),
    Input('beam-shape-in', 'value'),
    Input('beam-size-in', 'value'),
    Input('raster-x-in', 'value'),
    Input('raster-y-in', 'value'),
    Input('L-in', 'value'),
    Input('W-F-in', 'value'),
    Input('H-F-in', 'value'),
    Input('H-R-in', 'value'),
    prevent_initial_call = True
)
def create_json(n_clicks, beam_shape, beam_size, raster_x, raster_y, L, WF, HF, HR):

    return None

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
    State('example08A-files-check','value'),
    
    prevent_initial_call=True
)
def create_zip_report(data, n_clicks, 
                    xrdml_contents,xrdml_fnames,
                    instprm_contents,instprm_fname,
                    cif_contents,cif_fnames,
                    use_default_files, use_example05_files,
                    use_example06_files, use_example08A_files):
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
    elif use_example08A_files not in [None, []] and use_example08A_files[0] == 1:
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
