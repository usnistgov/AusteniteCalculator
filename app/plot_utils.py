import base64
import io
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.colors as mcolors

def create_encoded_plots(pk_fit_res,mcmc_df_dict):
    matplotlib.use('agg')
    
    # need to initialize plots with multiple return plots
    to_return = {
        'raw_intensity_plot':{},
        'fitted_intensity_plot':{}
    }

    image_prefix = 'data:image/png;base64,'

    full_results_table = pk_fit_res['full_results_table']
    dset_names = np.unique(full_results_table.sample_index)

    for i,val in enumerate(dset_names):

        # raw intensities plot
        name = 'raw_intensity_plot'
        tmpfile = io.BytesIO()
        plt.plot(pk_fit_res['two_thetas']['Dataset_' + val],pk_fit_res['fit_points']['Dataset_' + val][0])
        plt.title('Raw Intensities')
        plt.xlabel('Two Theta')
        plt.ylabel('Intensity')
        plt.savefig(tmpfile, format='png')
        tmpfile.seek(0) # go to beginning of buffer
        to_return[name]['Dataset_' + val] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
        plt.clf()

        # fitted intensities plot
        name = 'fitted_intensity_plot'
        tmpfile = io.BytesIO()
        plt.plot(pk_fit_res['two_thetas']['Dataset_' + val],pk_fit_res['fit_points']['Dataset_' + val][0])
        plt.plot(pk_fit_res['two_thetas']['Dataset_' + val],pk_fit_res['fit_points']['Dataset_' + val][2])
        plt.title('Raw and Fitted Intensities')
        plt.xlabel('Two Theta')
        plt.ylabel('Intensity')
        plt.savefig(tmpfile, format='png')
        tmpfile.seek(0) # go to beginning of buffer
        to_return[name]['Dataset_' + val] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
        plt.clf()

    # normalized intensities plot
    name = 'normalized_intensities_plot'
    tmpfile = io.BytesIO()
    phases = full_results_table.Phase
    unique_phases = np.unique(phases)

    for i,phase in enumerate(unique_phases):
        inds = np.where(phases == phase)
        x = full_results_table.pos_fit.iloc[inds]
        y = full_results_table.n_int.iloc[inds]
        plt.scatter(x,y,label=phase)
        plt.hlines(np.mean(y),np.min(x),np.max(x),linestyles='dashed',colors=mcolors.TABLEAU_COLORS[list(mcolors.TABLEAU_COLORS.keys())[i]])

    plt.title('Normalized Intensities')
    plt.xlabel('Two Theta')
    plt.ylabel('Normalized Intensity')
    plt.savefig(tmpfile, format='png')
    tmpfile.seek(0) # go to beginning of buffer
    to_return[name] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
    plt.clf()

    # phase fraction
    name = 'phase_fraction_plot'
    tmpfile = io.BytesIO()
    breakpoint()
    for i,phase in enumerate(unique_phases):
        plt.hist(mcmc_df_dict['number_cells_df'].iloc[:,i],alpha=.5,density=True,bins=30,label=phase)
    plt.xlabel("Phase Fraction")
    plt.ylabel("Density")
    plt.title("Phase Fraction Histogram")
    plt.savefig(tmpfile, format='png')
    tmpfile.seek(0) # go to beginning of buffer
    to_return[name] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
    plt.clf()

    # phase conversion -- mass_frac
    name = 'phase_fraction_plot_mass_frac'
    tmpfile = io.BytesIO()
    for i,phase in enumerate(unique_phases):
        plt.hist(mcmc_df_dict['mass_frac_df'].iloc[:,i],alpha=.5,density=True,bins=30,label=phase)
    plt.xlabel("Phase Fraction")
    plt.ylabel("Density")
    plt.title("Phase Fraction Histogram")
    plt.savefig(tmpfile, format='png')
    tmpfile.seek(0) # go to beginning of buffer
    to_return[name] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
    plt.clf()

    # phase conversion -- vol_frac
    name = 'phase_fraction_plot_vol_frac'
    tmpfile = io.BytesIO()
    for i,phase in enumerate(unique_phases):
        plt.hist(mcmc_df_dict['vol_frac_df'].iloc[:,i],alpha=.5,density=True,bins=30,label=phase)
    plt.xlabel("Phase Fraction")
    plt.ylabel("Density")
    plt.title("Phase Fraction Histogram")
    plt.savefig(tmpfile, format='png')
    tmpfile.seek(0) # go to beginning of buffer
    to_return[name] = image_prefix + base64.b64encode(tmpfile.read()).decode('utf-8')
    plt.clf()


    return to_return
