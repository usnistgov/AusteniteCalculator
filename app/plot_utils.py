import base64
import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.colors as mcolors

def create_encoded_plots(pk_fit_res,mcmc_res):

    to_return = {}

    image_prefix = 'data:image/png;base64,'

    # raw intensities plot
    name = 'raw_intensity_plot'
    tmpfile = io.BytesIO()
    plt.plot(pk_fit_res['two_thetas']['Dataset: 1'],pk_fit_res['fit_points']['Dataset: 1'][0])
    plt.title('Raw Intensities')
    plt.xlabel('Two Theta')
    plt.ylabel('Intensity')
    plt.savefig(tmpfile, format='png')
    tmpfile.seek(0) # go to beginning of buffer
    to_return[name] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
    plt.clf()

    # fitted intensities plot
    name = 'fitted_intensity_plot'
    tmpfile = io.BytesIO()
    plt.plot(pk_fit_res['two_thetas']['Dataset: 1'],pk_fit_res['fit_points']['Dataset: 1'][0])
    plt.plot(pk_fit_res['two_thetas']['Dataset: 1'],pk_fit_res['fit_points']['Dataset: 1'][2])
    plt.title('Raw and Fitted Intensities')
    plt.xlabel('Two Theta')
    plt.ylabel('Intensity')
    plt.savefig(tmpfile, format='png')
    tmpfile.seek(0) # go to beginning of buffer
    to_return[name] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
    plt.clf()

    # normalized intensities plot
    name = 'normalized_intensities_plot'
    tmpfile = io.BytesIO()
    results_table = pk_fit_res['full_results_table']
    phases = results_table.Phase
    unique_phases = np.unique(phases)

    for i,phase in enumerate(unique_phases):
        inds = np.where(phases == phase)
        x = results_table.pos_fit.iloc[inds]
        y = results_table.n_int.iloc[inds]
        plt.scatter(x,y,label=phase)
        plt.hlines(np.mean(y),np.min(x),np.max(x),linestyles='dashed',colors=mcolors.TABLEAU_COLORS[list(mcolors.TABLEAU_COLORS.keys())[i]])

    plt.title('Normalized Intensities')
    plt.xlabel('Two Theta')
    plt.ylabel('Normalized Intensity')
    plt.savefig(tmpfile, format='png')
    tmpfile.seek(0) # go to beginning of buffer
    to_return[name] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
    plt.clf()

    # phase 
    name = 'phase_fraction_plot'
    tmpfile = io.BytesIO()
    for i,phase in enumerate(unique_phases):
        plt.hist(mcmc_res['mcmc_df'].iloc[:,i],alpha=.5,density=True,bins=30,label=phase)
    plt.xlabel("Phase Fraction")
    plt.ylabel("Density")
    plt.title("Phase Fraction Histogram")
    plt.savefig(tmpfile, format='png')
    tmpfile.seek(0) # go to beginning of buffer
    to_return[name] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
    plt.clf()

    return to_return