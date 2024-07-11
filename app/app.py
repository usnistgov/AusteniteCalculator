from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json
#import matplotlib.pyplot as plt
#import plotly
#import plotly.express as px

import sys
import platform
import os
import io
import base64
import re

# user created
import plot_utils
import compute_results
import compute_uncertainties

if platform.system() == 'Linux':
    sys.path.insert(0,'/root/g2full/GSASII/')
    inside_docker = True

elif re.search('creuzige',os.getcwd()):
    sys.path.insert(0, '/Users/creuzige/gsas2full/envs/gsas-AustCalc/GSASII/')


import GSASIIscriptable as G2sc
import GSASIIpath

# Use a specific version of GSAS-II for consistency
## Commenting out for now, GSAS svn server sometimes down

#try:
#    GSASIIpath.svnUpdateDir(version=5300,verbose=True)
#except Exception: #GSAS raises an execption if unable to connect to svn
#    print("Unable to update, using whichever version is installed")

app = Flask(__name__)

@app.route("/",methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/submit",methods=['POST'])
def submit():

    req = request.get_json()
    print(req)

    if req['radioValue'] == 'None':
        return jsonify({'res':'None'})

    else:
        datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname = compute_results.gather_example(req['radioValue'])

    with open(os.path.join(datadir, json_fname), 'r') as f:
        crystal_data = json.loads(f.read())

    print("Computing Cell Density")
    cell_dens_res = compute_results.compute_cell_density(cif_fnames,datadir,instprm_fname)

    print("Running Peak Fitting")
    pk_fit_res = compute_results.compute_peak_fitting(datadir,workdir,xrdml_fnames,instprm_fname,cif_fnames,crystal_data,G2sc)

    print("Computing peaks_dict")
    peaks_dict = compute_results.compute_peaks_dict(cif_fnames,pk_fit_res['results_table'],cell_dens_res['scattering_dict'],cell_dens_res['elem_fractions_dict'])

    print("Gathering Summarized Phase Info")
    graph_data_dict = compute_results.compute_summarized_phase_info(cell_dens_res['scattering_dict'],cell_dens_res['elem_fractions_dict'],peaks_dict)

    print("Computing crystallites illuminated...")
    cryst_ill_res = compute_results.compute_crystallites_illuminated(crystal_data,peaks_dict,pk_fit_res['results_table'],pk_fit_res['phase_frac'])

    print("Computing mass fraction and volume fracation conversion factors...")
    conversions = compute_results.get_conversions(pk_fit_res['phase_frac'],
                                                  cell_dens_res['cell_masses_dict'],
                                                  cell_dens_res['cell_volumes_dict'])

    print("Running MCMC")
    mcmc_df_dict, param_table, pf_table = compute_results.run_mcmc(pk_fit_res['results_table'],number_mcmc_runs=1000,conversions=conversions)

    # combine all results into a dictionary to send to browser
    # param_table has the uncertainty parameters from mcmc result
    # pf_table has the phase fraction with conversions
    # results_table is the combined fit and theoretical data
    # mcmc_df are all the simulated phase fractions (by unit cell)
    all_results = {'two_thetas':pk_fit_res['two_thetas'],
                   'fit_points':pk_fit_res['fit_points'],
                   'param_table':param_table.to_dict(orient='list'),
                   'param_table_html':param_table.to_html(),
                   'pf_table':pf_table.to_dict(orient='list'),
                   'pf_table_html':pf_table.to_html(),
                   'results_table':pk_fit_res['full_results_table'].to_dict(orient='list'),
                   'results_table_html':pk_fit_res['full_results_table'].to_html(),
                   'mcmc_df':mcmc_df_dict['number_cells_df'].to_dict(orient='list'),
                   'unique_phases':np.unique(pk_fit_res['full_results_table'].Phase).tolist(),
                   'n_dsets':np.unique(pk_fit_res['full_results_table'].sample_index).shape[0]}

    # quick and dirty way to export all
    with open("export-all.json", "w") as outfile:
        json.dump(all_results, outfile)



    return jsonify(all_results)

@app.route("/instprm_json",methods=["POST"])
def instprm_json():
    request_var = request.get_json()
    return "The value you submitted to the instprm route is " + request_var['var']

@app.route("/cryst",methods=["POST"])
def cryst():
    request_var = request.get_json()
    return "The value you submitted to the cryst route is " + request_var['var']

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=8050,debug=True)
