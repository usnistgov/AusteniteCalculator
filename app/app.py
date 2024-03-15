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

    # let's try to just get example 5 working
    datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname = compute_results.gather_example("Example05")

    with open(os.path.join(datadir, json_fname), 'r') as f:
        crystal_data = json.loads(f.read())

    print("Computing Interaction Volume")
    int_vol_res = compute_results.compute_interaction_volume(cif_fnames,datadir,instprm_fname)

    print("Running Peak Fitting")
    pk_fit_res = compute_results.compute_peak_fitting(datadir,workdir,xrdml_fnames,instprm_fname,cif_fnames,crystal_data,G2sc)

    print("Computing peaks_dict")
    peaks_dict = compute_results.compute_peaks_dict(cif_fnames,pk_fit_res['results_table'],int_vol_res['scattering_dict'],int_vol_res['elem_fractions_dict'])

    print("Gathering Summarized Phase Info")
    graph_data_dict = compute_results.compute_summarized_phase_info(int_vol_res['scattering_dict'],int_vol_res['elem_fractions_dict'],peaks_dict)

    print("Computing crystallites illuminated...")
    cryst_ill_res = compute_results.compute_crystallites_illuminated(crystal_data,peaks_dict,pk_fit_res['results_table'],pk_fit_res['phase_frac'])

    print("Running MCMC")
    mcmc_res = compute_results.run_mcmc(pk_fit_res['results_table'],fit_vi=False,number_mcmc_runs=1000)
    pf_table = compute_uncertainties.generate_pf_table(mcmc_res['mcmc_df'],np.unique(pk_fit_res['full_results_table'].Phase))

    encoded_plots = plot_utils.create_encoded_plots(pk_fit_res,mcmc_res)

    # combine all results into a dictionary to send to browser
    all_results = {'results_table_html':pk_fit_res['full_results_table'].to_html(justify='left'),
                   'param_table_html':mcmc_res['param_table'].to_html(justify='left'),
                   'pf_table_html':pf_table.to_html(justify='left'),
                   'results_table':pk_fit_res['full_results_table'].to_dict(orient='list'),
                   'unique_phases':np.unique(pk_fit_res['full_results_table'].Phase).tolist(),
                   'encoded_plots':encoded_plots}


    return jsonify(all_results)


if __name__ == '__main__':
   app.run(host='0.0.0.0',port=8050,debug=True)
