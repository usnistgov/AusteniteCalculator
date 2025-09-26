from flask import Flask, render_template, request, jsonify, session, send_file
import pandas as pd
import numpy as np
import json
import secrets
import tempfile
import zipfile
#import matplotlib.pyplot as plt
#import plotly
#import plotly.express as px

import sys
import platform
import os
import io
import base64
import re
import pickle
import time
import logging

# user created
import plot_utils
import compute_results
import compute_uncertainties

if platform.system() == 'Linux':
    sys.path.insert(0,'/root/g2full/GSAS-II/GSASII/')
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
logging.basicConfig(stream=log_buffer, level=logging.INFO)

# set up app
app = Flask(__name__)
app.secret_key = "super_secret_key"

@app.route("/",methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/submit",methods=['POST'])
def submit():
    """
    Initiate phase fraction calculations when user presses the 'Submit' button on the app. Sections describe various steps (and use the same text as comment headers).
    
    * Create dictionary to hold error logs
    * Choose datafiles to run and set paths
    * Collect version information
    * Compute Cell Density
    * Run Peak Fitting
    * Compute crystallites illuminated
    * Run MCMC
    * Collect data to display
    * Save submission and all_results
    
    
    Returns:
        all_results (Dictionary): JSON-ified dictionary with all results
    
    """
    print("####  Initializing Submission")
    Submission={}

    req = request.get_json()
    print(req)
    logger.info(req)

    #### Create dictionary to hold error logs
    print("####  Create dictionary to hold error logs")
    logger.info("Create dictionary to hold error logs")
    
    error_dict = {'file_upload':False,
                  'interaction_param_data':False,  # CHECKED
                    'Version':False, #Checked
                    'cell_density':False,
                    'peak_fitting':False,
                    'peak_dict':False,
                    'phase_info':False,
                    'crystallites_illuminated':False,
                    'conversions':False,
                    'mcmc':False}

    #### Choose datafiles to run and set paths
    print("####  Choose datafiles to run and set paths")
    logger.info("Choose datafiles to run and set paths")   
    
    # upload user files if indicated to do so
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

    # otherwise, prepare an example file for analysis
    else:
        datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname = compute_results.gather_example(req['radioValue'])


    # Need to figure out how to merge crystal_data with phase info
    try:
        with open(os.path.join(datadir, json_fname), 'r') as f:
            interaction_param_data = json.loads(f.read())

    except Exception as e:
        error_dict['interaction_param_data'] = type(e).__name__ + ': ' + str(e)


    Submission["Phase_Info"]={}
    # was crystal
    Submission["Phase_Info"]["Interaction_Parameters"]=interaction_param_data

    #Maybe these should be moved into .gather_example?
    # Would need to pass Submission along
    Submission["File_Paths"]={}
    Submission["File_Paths"]["Data_Directory"]=datadir
    Submission["File_Paths"]["Working_Directory"]=workdir
    Submission["File_Paths"]["Cif_Filenames"]=cif_fnames
    Submission["File_Paths"]["Diffraction_Filenames"]=xrdml_fnames
    Submission["File_Paths"]["Instrument_Filename"]=instprm_fname
    Submission["File_Paths"]["JSON_Filename"]=json_fname


    #### Collect version information
    print("####  Collecting Version information")
    logger.info("Collecting Version information")
    
    try:
        Submission["Version"] = compute_results.version_summary()
    except Exception as e:
        error_dict['Version'] = type(e).__name__ + ': ' + str(e)

    #### Compute Cell Density
    print("####  Compute Cell Density")
    logger.info("Compute Cell Density")
    # probably need to merge dataframes later
    # Should I update this later?
    try:
        Submission=compute_results.compute_cell_density(Submission)
    except Exception as e:
        error_dict['cell_density'] = type(e).__name__ + ': ' + str(e)

    #### Run Peak Fitting
    print("####  Run Peak Fitting")
    logger.info("Run Peak Fitting")
    try:
        Submission = compute_results.compute_peak_fitting(G2sc, Submission)
    except Exception as e:
        error_dict['peak_fitting'] = type(e).__name__ + ': ' + str(e)

    print("\n****************************************\n",Submission.keys())
 
    #### Compute crystallites illuminated
    print("####  Compute crystallites illuminated")
    logger.info("Compute crystallites illuminated")

    try:
        Submission = compute_results.compute_crystallites_illuminated(Submission)
    except Exception as e:
        error_dict['crystallites_illuminated'] = type(e).__name__ + ': ' + str(e)


    #### Run MCMC
    print("####  Run MCMC")
    logger.info("Run MCMC")
    try:
        Submission = compute_results.run_mcmc2(Submission,req['sumFiles'],number_mcmc_runs=1000)
    except Exception as e:
        error_dict['mcmc'] = type(e).__name__ + ': ' + str(e)

    log_text = log_buffer.getvalue()
    
    
    #### Collect data to display
    print("####  Collect data to display")
    logger.info("Collect data to display")
    
    # Escape application if there are error messages
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

        all_results=compute_results.package_for_export(Submission)

        all_results['errors']=False
        all_results['error_dict']=error_dict
        all_results['logs']=log_text

    print("Keys for all_results:")
    print(all_results.keys())
    #breakpoint()


    # quick and dirty way to export all
    #with open("export-all.json", "w") as outfile:
    #    json.dump(all_results, outfile)

    # Export all data (Submission) to file
    # the json file where the output must be stored

    # Save submission and all_results
    print("####  Save submission and all_results")
    logger.info("Save submission and all_results")

    timestamp=time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())

    with open('Submission'+timestamp+'.pickle', 'wb') as f:
        pickle.dump(Submission, f, protocol=4)
    with open('Results'+timestamp+'.pickle', 'wb') as f:
        pickle.dump(all_results, f, protocol=4)

        # quick and dirty way to export all
        #with open("export-all.json", "w") as outfile:
        #    json.dump(all_results, outfile)

    user_id = secrets.token_hex(6)
    temp_dir = tempfile.mkdtemp(prefix='session_' + user_id, dir="/tmp")
    session["download_id"] = temp_dir

    fp = os.path.join(temp_dir,'Submission.pickle')
    with open(fp,'wb') as f:
        pickle.dump(Submission, f, protocol=4)

    fp = os.path.join(temp_dir,'all_results.pickle')
    with open(fp,'wb') as f:
        pickle.dump(all_results, f, protocol=4)

    #breakpoint()

    return jsonify(all_results)

@app.route("/instprm_json",methods=["POST"])
def instprm_json():
    request_var = request.get_json()
    return "The value you submitted to the instprm route is " + request_var['var']

@app.route("/cryst",methods=["POST"])
def cryst():
    request_var = request.get_json()
    return "The value you submitted to the cryst route is " + request_var['var']

@app.route("/download",methods=['GET'])
def download():

    temp_dir = session.get("download_id")

    if not temp_dir or not os.path.exists(temp_dir):
        return "No file to download", 404
    
    zip_path = tempfile.mktemp(suffix=".zip", dir="/tmp")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, temp_dir)
                zipf.write(abs_path, rel_path)

    return send_file(zip_path, as_attachment=True, download_name="files.zip")

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=8050,debug=True)
