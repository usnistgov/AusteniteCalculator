import compute_results
from testing_data_setup import dataSetup
import pytest
import warnings
# -*- coding: utf-8 -*-

# dash imports
from fileinput import filename
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_file
#from dash.dash_table.Format import Format, Scheme, Trim # Tried to set format, failed...

# plotting
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# utils
import base64
import io
import os
import platform
import re
import sys
import flask
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
dataGrabber = None

def setup_module(module):
    print('*****SETUP******')
    global dataGrabber
    dataGrabber = dataSetup

def test_EX1():
    datadir = '../server_default_datadir' 
    cif_fnames = ['austenite-Duplex.cif','ferrite-Duplex.cif']
    workdir = '../server_workdir'
    xrdml_fname = 'Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper_power.xrdml'
    instprm_fname = 'TestCalibration.instprm'
    master_data = '../server_default_datadir/EX1_master.txt'
    inference_method = 'paul_mandel'
    check_list, phases = dataGrabber.read_data(master_data)
    fig1, fig2, results_df, ni_fig, two_theta_fig, phase_frac_DF, uncert_DF, pf_uncertainty_fig, pf_uncertainty_table = compute_results.compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc,inference_method)
    
    keys = check_list.keys()
    for i in range(len(keys)):
        for j in range(phases):
            if(i == 4):
                continue
            elif(i == 0 or i == 3):
                assert check_list.loc[j, keys[i]] == phase_frac_DF.loc[j, keys[i]]
            else:
                if(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= 0.001 and abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s are not exact, but within 5 percent of one another" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                elif(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s have a difference of greater the 5 percent" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                assert abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05
    
def test_EX2():
    datadir = '../ExampleData/Example02' 
    cif_fnames = ['austenite-Duplex.cif','ferrite-Duplex.cif']
    workdir = '../server_workdir'
    xrdml_fname = 'Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper_power.xrdml'
    instprm_fname = 'TestCalibration.instprm'
    master_data = '../server_default_datadir/EX2_master.txt'
    inference_method = 'paul_mandel'
    check_list, phases = dataGrabber.read_data(master_data)
    fig1, fig2, results_df, ni_fig, two_theta_fig, phase_frac_DF, uncert_DF, pf_uncertainty_fig, pf_uncertainty_table = compute_results.compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc,inference_method)
    
    keys = check_list.keys()
    for i in range(len(keys)):
        for j in range(phases):
            if(i == 4):
                continue
            elif(i == 0 or i == 3):
                assert check_list.loc[j, keys[i]] == phase_frac_DF.loc[j, keys[i]]
            else:
                if(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= 0.001 and abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s are not exact, but within 5 percent of one another" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                elif(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s have a difference of greater the 5 percent" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                assert abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05
    
def test_EX3():
    datadir = '../server_default_datadir' 
    cif_fnames = ['austenite-Duplex.cif','ferrite-Duplex.cif']
    workdir = '../server_workdir'
    xrdml_fname = 'Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper_power.xrdml'
    instprm_fname = 'TestCalibration.instprm'
    master_data = '../server_default_datadir/EX1_master.txt'
    inference_method = 'paul_mandel'
    check_list, phases = dataGrabber.read_data(master_data)
    fig1, fig2, results_df, ni_fig, two_theta_fig, phase_frac_DF, uncert_DF, pf_uncertainty_fig, pf_uncertainty_table = compute_results.compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc,inference_method)
    
    keys = check_list.keys()
    for i in range(len(keys)):
        for j in range(phases):
            if(i == 4):
                continue
            elif(i == 0 or i == 3):
                assert check_list.loc[j, keys[i]] == phase_frac_DF.loc[j, keys[i]]
            else:
                if(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= 0.001 and abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s are not exact, but within 5 percent of one another" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                elif(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s have a difference of greater the 5 percent" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                assert abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05
    
def test_EX4():
    datadir = '../server_default_datadir' 
    cif_fnames = ['austenite-Duplex.cif','ferrite-Duplex.cif']
    workdir = '../server_workdir'
    xrdml_fname = 'Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper_power.xrdml'
    instprm_fname = 'TestCalibration.instprm'
    master_data = '../server_default_datadir/EX1_master.txt'
    inference_method = 'paul_mandel'
    check_list, phases = dataGrabber.read_data(master_data)
    fig1, fig2, results_df, ni_fig, two_theta_fig, phase_frac_DF, uncert_DF, pf_uncertainty_fig, pf_uncertainty_table = compute_results.compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc,inference_method)
    
    keys = check_list.keys()
    for i in range(len(keys)):
        for j in range(phases):
            if(i == 4):
                continue
            elif(i == 0 or i == 3):
                assert check_list.loc[j, keys[i]] == phase_frac_DF.loc[j, keys[i]]
            else:
                if(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= 0.001 and abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s are not exact, but within 5 percent of one another" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                elif(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s have a difference of greater the 5 percent" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                assert abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05
    

def test_EX5():
    datadir = '../ExampleData/Example05'
    cif_fnames = ['austenite-SRM487.cif','ferrite-SRM487.cif']
    workdir = '../server_workdir'
    xrdml_fname = 'E211110-AAC-001_019-000_exported.csv'
    instprm_fname = 'BrukerD8_E211110.instprm'
    master_data = '../ExampleData/Example05/EX5_master.txt'
    inference_method = 'paul_mandel'
    check_list, phases = dataGrabber.read_data(master_data)
    fig1, fig2, results_df, ni_fig, two_theta_fig, phase_frac_DF, uncert_DF, pf_uncertainty_fig, pf_uncertainty_table = compute_results.compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc,inference_method)
    
    keys = check_list.keys()
    for i in range(len(keys)):
        for j in range(phases):
            if(i == 4):
                continue
            elif(i == 0 or i == 3):
                assert check_list.loc[j, keys[i]] == phase_frac_DF.loc[j, keys[i]]
            else:
                if(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= 0.001 and abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s are not exact, but within 5 percent of one another" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                elif(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s have a difference of greater the 5 percent" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                assert abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05
    

def test_EX6():
    datadir = '../ExampleData/Example06'
    cif_fnames = ['alpha-prime-martensite-SRI.cif','epsilon-martensite-SRI.cif','austenite-SRI.cif']
    workdir = '../server_workdir'
    xrdml_fname = 'Example06_simulation_generation_data.csv'
    instprm_fname = 'BrukerD8_E211110.instprm'
    master_data = '../ExampleData/Example06/EX6_master.txt'
    inference_method = 'paul_mandel'
    check_list, phases = dataGrabber.read_data(master_data)
    fig1, fig2, results_df, ni_fig, two_theta_fig, phase_frac_DF, uncert_DF, pf_uncertainty_fig, pf_uncertainty_table = compute_results.compute(datadir,workdir,xrdml_fname,instprm_fname,cif_fnames,G2sc,inference_method)
    
    keys = check_list.keys()
    for i in range(len(keys)):
        for j in range(phases):
            if(i == 4):
                continue
            elif(i == 0 or i == 3):
                assert check_list.loc[j, keys[i]] == phase_frac_DF.loc[j, keys[i]]
            else:
                if(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= 0.001 and abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s are not exact, but within 5 percent of one another" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                elif(abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) >= check_list.loc[j, keys[i]] * 0.05):
                    warning_string = "Values for %s have a difference of greater the 5 percent" % keys[i]
                    warnings.warn(UserWarning(warning_string))
                assert abs(check_list.loc[j, keys[i]] - phase_frac_DF.loc[j, keys[i]]) <= check_list.loc[j, keys[i]] * 0.05
    