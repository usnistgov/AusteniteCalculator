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
import logging

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
#    logger.info("Unable to update, using whichever version is installed")

# set up logger
logger = logging.getLogger(__name__)
log_buffer = io.StringIO()
logging.basicConfig(stream=log_buffer,encoding='utf-8', level=logging.INFO)

# set up app
app = Flask(__name__)

@app.route("/",methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/submit",methods=['POST'])
def submit():

    req = request.get_json()
    logger.info(req)

    # dictionary to hold error logs
    error_dict = {'file_upload':False,
                  'crystal_data':False,
                    'version':False,
                    'cell_density':False,
                    'peak_fitting':False,
                    'peak_dict':False,
                    'phase_info':False,
                    'crystallites_illuminated':False,
                    'conversions':False,
                    'mcmc':False}

    if req['radioValue'] == 'uploaded_files':

        try:
            datadir = '../server_datadir'
            cif_fnames = list(req['fileUploads']['cif-file'].keys())
            workdir = '../server_workdir'
            xrdml_fnames = list(req['fileUploads']['xrdml-files'].keys())
            instprm_fname = list(req['fileUploads']['instprm-file'].keys())[0]
            json_fname = list(req['fileUploads']['cryst-illum-file'].keys())[0]

            # loop through all file types
            for file_type in req['fileUploads'].keys():

                # loop through all files in the file type
                for file in req['fileUploads'][file_type].keys():

                    # write file with the file name 
                    with open(datadir + '/' + file,'w') as f:
                        f.write(req['fileUploads'][file_type][file])

        except Exception as e:
            error_dict['file_upload'] = type(e).__name__ + ': ' + str(e)

    else:
        datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname = compute_results.gather_example(req['radioValue'])

    try:
        with open(os.path.join(datadir, json_fname), 'r') as f:
            crystal_data = json.loads(f.read())

    except Exception as e:
        error_dict['crystal_data'] = type(e).__name__ + ': ' + str(e)


    logger.info("Collecting Version information")
    try:
        version_DF = compute_results.version_summary()
    except Exception as e: 
        error_dict['version'] = type(e).__name__ + ': ' + str(e)

    logger.info("Computing Cell Density")
    try:
        cell_dens_res = compute_results.compute_cell_density(cif_fnames,datadir,instprm_fname)
    except Exception as e: 
        error_dict['cell_density'] = type(e).__name__ + ': ' + str(e)

    logger.info("Running Peak Fitting")
    try:
        pk_fit_res = compute_results.compute_peak_fitting(datadir,workdir,xrdml_fnames,instprm_fname,cif_fnames,crystal_data,G2sc)
    except Exception as e: 
        error_dict['peak_fitting'] = type(e).__name__ + ': ' + str(e)

    logger.info("Computing peaks_dict")
    try:
        peaks_dict = compute_results.compute_peaks_dict(cif_fnames,pk_fit_res['results_table'],cell_dens_res['scattering_dict'],cell_dens_res['elem_fractions_dict'])
    except Exception as e: 
        error_dict['peak_dict'] = type(e).__name__ + ': ' + str(e)

    logger.info("Gathering Summarized Phase Info")
    try:
        graph_data_dict = compute_results.compute_summarized_phase_info(cell_dens_res['scattering_dict'],cell_dens_res['elem_fractions_dict'],peaks_dict)
    except Exception as e: 
        error_dict['phase_info'] = type(e).__name__ + ': ' + str(e)

    logger.info("Computing crystallites illuminated...")
    # Need to update the full results table, but issues with dict/DF 
 #   cryst_ill_res, pk_fit_res['full_results_table'] = compute_results.compute_crystallites_illuminated(crystal_data,peaks_dict,pk_fit_res['results_table'],pk_fit_res['phase_frac'])
    try:
        cryst_ill_res = compute_results.compute_crystallites_illuminated(crystal_data,peaks_dict,pk_fit_res['results_table'],pk_fit_res['phase_frac'])
    except Exception as e: 
        error_dict['crystallites_illuminated'] = type(e).__name__ + ': ' + str(e)

    logger.info("Computing mass fraction and volume fracation conversion factors...")
    try:
        conversions = compute_results.get_conversions(pk_fit_res['phase_frac'],
                                                    cell_dens_res['cell_masses_dict'],
                                                    cell_dens_res['cell_volumes_dict'])
    except Exception as e: 
        error_dict['conversions'] = type(e).__name__ + ': ' + str(e)


    logger.info("Running MCMC")
    try:
        mcmc_df_dict, param_table, pf_table = compute_results.run_mcmc(pk_fit_res['results_table'],number_mcmc_runs=1000,conversions=conversions)
    except Exception as e: 
        error_dict['mcmc'] = type(e).__name__ + ': ' + str(e)

    log_text = log_buffer.getvalue()

    if any(error_dict.values()):

        all_results = {
            'errors':True,
            'error_dict':error_dict,
            'logs':log_text
        }

    else:
        # combine all results into a dictionary to send to browser
        # param_table has the uncertainty parameters from mcmc result
        # pf_table has the phase fraction with conversions
        # results_table is the combined fit and theoretical data
        # mcmc_df are all the simulated phase fractions (by unit cell)
        all_results = {'errors':False,
                       'conversion_table':conversions.to_dict(orient='list'),
                        'version_html':version_DF.to_html(justify='left', index=False),
                        'two_thetas':pk_fit_res['two_thetas'],
                        'fit_points':pk_fit_res['fit_points'],
                        'cryst_ill_res':cryst_ill_res['crystallites_dict'],
                        #'cryst_ill_res':cryst_ill_res,
                        # issues since user flags are per data set
                        #'user_flags':pk_fit_res['user_flags'],
                        # Create dictionary of html tables
                        # Have it be a choice of the which dataset
                        #'user_flags_html':pk_fit_res['user_flags'].to_html(justify='left'),
                        'param_table':param_table.to_dict(orient='list'),
                        'param_table_html':param_table.to_html(justify='left'),
                        'pf_table':pf_table.to_dict(orient='list'),
                        'pf_table_html':pf_table.to_html(justify='left', index=False),
                        'results_table':pk_fit_res['full_results_table'].to_dict(orient='list'),
                        # changing to pass to full results, now a dict
                        #'results_table':pk_fit_res['full_results_table'],
                        'results_table_html':pk_fit_res['full_results_table'].to_html(justify='left'),
                        # Issues with structure of graph_data_table
                        # Maybe due to pandas dataframes nested inside
                        #'graph_data_table':graph_data_dict,
                        'mcmc_dict':mcmc_df_dict,
                        'unique_phases':np.unique(pk_fit_res['full_results_table'].Phase).tolist(),
                        'n_dsets':np.unique(pk_fit_res['full_results_table'].sample_index).shape[0],
                        'logs':log_text}

        # quick and dirty way to export all
        #with open("export-all.json", "w") as outfile:
        #    json.dump(all_results, outfile)

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
