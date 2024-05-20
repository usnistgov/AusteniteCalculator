import numpy as np
import pandas as pd
from cmdstanpy import CmdStanModel
import sys



def get_unique_phases(results_table):

    """
    *ADD*

    Parameters:
        mu_samps: *ADD*
        conversion_vec: *ADD*


    Returns:
        | *ADD*
        |

    Raises:


    """

    intables = list(results_table.values())

    indata = pd.concat(intables,axis=0).reset_index(drop=True)

    return np.unique(indata.Phase)

def concat_results_tables(results_table,from_records=False):

    """
    Combine tables if there are multiple xrd records

    Parameters:
        results_table: *ADD*
        from_records: *ADD*


    Returns:
        | *ADD*
        |

    Raises:


    """
    intables = list(results_table.values())

    # create numeric sample ids
    for ii, val in enumerate(intables):

        if from_records:
            intables[ii] = pd.DataFrame.from_records(intables[ii][0])

        intables[ii] = intables[ii].loc[intables[ii]['Peak_Fit_Success'],:]
        intables[ii]['sample_id'] = ii+1

    indata = pd.concat(intables,axis=0).reset_index(drop=True)

    return indata

def run_stan(results_table,number_mcmc_runs,fit_variational=False):
    """
    Runs an external script using Stan (https://mc-stan.org/) to return estimates
    of the phase fractions. Largely uses normalized intensity data. Uses Bayesian
    priors and data to estimate uncertainties express draws via a posterior distrubtion

    Samples in this case implies xrd files/scans

    Parameters:
        results_table: Dictionary of 'pd.DataFrame's, e.g., results_table['Dataset_1']
        number_mcmc_runs: Number of MCMC warmup runs. 2000 runs are kept total, but these are used as a 'warm-up' for the sampler.


    Returns:
        | *ADD*
        |

    Raises:


    """
    indata = concat_results_tables(results_table)

    # Create a new dataframe with a selection of data
    mydf = pd.DataFrame({
        'I':indata.int_fit,
        'R':indata.R_calc,
        'sigma_I':indata.u_int_fit,
        'u_int_count':indata.u_int_count,
        'u_cryst_diff':indata.u_cryst_diff,
        'phases':indata.Phase,
        'two_th':indata.two_theta,
        'sample_id':indata.sample_id,
        'IR':indata.n_int # Check if this keeps the texture corrections
    })

    # create numeric phase id's
    mydf['phase_id'] = 0
    unique_phases = np.unique(mydf.phases)

    for ii, pn in enumerate(unique_phases):
        mydf.loc[mydf['phases'] == pn,'phase_id'] = ii+1

    # compute variation in normalized intensities
    # commented out, use n_int directly so that texture variation is included
    # Commented out after merge
    #mydf['IR'] = mydf.I / mydf.R

    # Is this even used?
    # not sure if we should use texture corrected values or not
    mydf['sig_IR'] = mydf['sigma_I']/mydf.R

    # compute Bayesian prior distributions
    # prior_sample_scale for variation between multiple xrd scans
    if  len(results_table) > 1:
        prior_sample_scale = np.std(mydf.IR)

    else:
        prior_sample_scale = None

    # prior_exp_scale = variation based on peak to peak variation
    prior_exp_scale = np.mean(mydf.groupby(['sample_id','phase_id']).IR.std())
    
    # prior_location is the inital location (value) of the data
    prior_location = np.array(mydf.groupby('phase_id').IR.mean())

    print("Bayesian Prior Estimates")
    print("Prior sample scale: {}".format(prior_sample_scale))
    print("Prior exp scale: {}".format(prior_exp_scale))
    print("Prior location: {}".format(prior_location))
    print("Prior scale: {}".format(np.std(mydf.IR)))

    ### Code for the single sample case
    if len(results_table) == 1:

        # stan

        #check OS to determine which stan executable to use
        # Should this be a try/except block?   https://stackoverflow.com/questions/17322208/multiple-try-codes-in-one-block
        
        if sys.platform.startswith('win'): # windows -- have not tested this in a while
            #Untested
            exe_file = '../stan_files/one_sample.exe'

        elif sys.platform.startswith('darwin'): # MacOS
            exe_file = '../stan_files/one_sample'

        elif sys.platform.startswith('linux'):
            # Untested.  If we include precompiled files, we may need to change the filename
            exe_file = '../stan_files/one_sample'

        else:
            print("Not a recognized OS")

        model = CmdStanModel(stan_file='../stan_files/one_sample.stan')
        #model = CmdStanModel(exe_file=exe_file)

        stan_data = {
            "N":mydf.shape[0],
            "N_phases":len(np.unique(mydf.phases)),
            "Y":mydf.IR,
            "phase":mydf.phase_id,
            "prior_scale":np.std(mydf.IR), # standard deveiation
            "prior_exp_scale":prior_exp_scale, # mean of the standard deviations
            "prior_location":prior_location, # mean value
            "u_int_fit":mydf.sigma_I/mydf.R,
            "u_int_count":mydf.u_int_count/mydf.R,
            "u_cryst_diff":mydf.u_cryst_diff/mydf.R
        }


        # Runs 4*2000 samples anyway, number of mcmc runs is warmup period?
        fit = model.sample(data=stan_data,
                            chains=4,
                            iter_warmup=number_mcmc_runs,
                            iter_sampling=2000)


    ### Code for the multiple sample case
    elif len(results_table) > 1:

        # check OS to determine which stan executable to use
        # Should this be a try/except block?    https://stackoverflow.com/questions/17322208/multiple-try-codes-in-one-block
        if sys.platform.startswith('win'): #windows
            #Untested
            exe_file = '../stan_files/multiple_samples.exe'

        elif sys.platform.startswith('darwin'): # MacOS
            exe_file = '../stan_files/multiple_samples'

        elif sys.platform.startswith('linux'):
            # Untested.  If we include precompiled files, we may need to change the filename
            exe_file = '../stan_files/multiple_samples'

        else:
            print("Not a recognized OS")

        # create numeric grouping variable for sample/group combo (stan needs ordered sequential numeric index)
        mydf['phase_sample'] = mydf['phase_id'].astype("string") + mydf['sample_id'].astype("string")
        mydf['phase_sample_id'] = 0

        unique_phase_sample_ids = pd.unique(mydf['phase_sample'])

        for ii,the_id in enumerate(unique_phase_sample_ids):

            mydf.loc[mydf['phase_sample'] == the_id,'phase_sample_id'] = ii + 1

        model = CmdStanModel(stan_file = '../stan_files/multiple_samples.stan')
        #model = CmdStanModel(exe_file=exe_file)
 
        stan_data = {
            "N":mydf.shape[0],
            "N_samples":len(np.unique(mydf.sample_id)),
            "N_phases":len(np.unique(mydf.phases)),
            "N_phase_samples":len(np.unique(mydf.phase_sample_id)),
            "Y":mydf.IR,
            "phase":mydf.phase_id,
            "group":mydf.sample_id,
            "phase_sample_id":mydf.phase_sample_id,
            "prior_scale":np.std(mydf.IR),
            "prior_sample_scale":prior_sample_scale,
            "prior_exp_scale":prior_exp_scale,
            "prior_location":prior_location,
            "u_int_fit":mydf.sigma_I/mydf.R,
            "u_int_count":mydf.u_int_count/mydf.R,
            "u_cryst_diff":mydf.u_cryst_diff/mydf.R
        }



        fit = model.sample(data=stan_data,
                           chains=4,
                           iter_warmup=number_mcmc_runs,
                           iter_sampling=2000)

    mcmc_df = fit.draws_pd()
    print(mcmc_df.info(memory_usage=True))

    mcmc_df.drop(inplace=True,columns = mcmc_df.columns[mcmc_df.columns.str.contains("(__)|(effect)",regex=True)])

    phase_cols = mcmc_df.loc[:,mcmc_df.columns.str.contains("phase_mu")]
    ni_sum = np.sum(phase_cols,axis=1)
    for i in range(phase_cols.shape[1]):
        phase_cols.iloc[:,i] = phase_cols.iloc[:,i]/ni_sum

    mcmc_df.loc[:,mcmc_df.columns.str.contains("phase_mu")] = phase_cols

    return mcmc_df

def generate_pf_table(mcmc_df_dict,unique_phase_names):
    """
    *ADD*

    Parameters:
        mu_samps: *ADD*
        conversion_vec: *ADD*


    Returns:
        | *ADD*
        |

    Raises:


    """
    full_dict = {}

    for conversion_name in mcmc_df_dict.keys():

        mcmc_df = mcmc_df_dict[conversion_name]

        mu_res = np.array(mcmc_df.loc[:,mcmc_df.columns.str.contains('phase_mu')])
        n_phase = mu_res.shape[1]
        quantiles = np.zeros((n_phase,2))

        # table to store phase fraction estimates and 95% credible intervals
        pf_table = pd.DataFrame({
            'Phase':unique_phase_names,
            'Phase Fraction Estimate':0.0,
            'Phase Fraction (Lower 95%)':0.0,
            'Phase Fraction (Upper 95%)':0.0
        })

        for j,ph in enumerate(unique_phase_names):

            quantiles[j,:] = np.quantile(mu_res[:,j],(.025,.975))

            pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction Estimate'] = np.mean(mu_res[:,j])
            pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction (Lower 95%)'] = np.quantile(mu_res[:,j],.025)
            pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction (Upper 95%)'] = np.quantile(mu_res[:,j],.975)

        full_dict[conversion_name] = pf_table
        pf_table['Conversion Type'] = conversion_name

    pf_table = pd.concat(full_dict,ignore_index=True)

    return pf_table

def generate_param_table(mcmc_df,unique_phase_names,results_table):
    """
    *ADD*

    Parameters:
        mu_samps: *ADD*
        conversion_vec: *ADD*


    Returns:
        | A pandas DataFrame with rows for each phase.
        | Columns for each source of variability

    Raises:


    """
    mu_res = np.array(mcmc_df.loc[:,mcmc_df.columns.str.contains('phase_mu')])
    n_phase = mu_res.shape[1]
    multiple_samples = 'sigma_sample' in mcmc_df.columns

    # table to hold parameter estimates for sources of uncertainty
    param_table = pd.DataFrame({
        'Phase':unique_phase_names,
        'Experimental Error Variability':np.zeros(n_phase),
        'X-ray Count Variability':np.zeros(n_phase),
        'Parameter Fit Variability':np.zeros(n_phase),
        'Crystallites Diffracted Variability':np.zeros(n_phase)
    })

    if multiple_samples:
        param_table['Sample Variability'] = np.zeros(n_phase)

    results_table = results_table.loc[results_table['Peak_Fit_Success'],:]

    for ii,ph in enumerate(unique_phase_names):

        t_sigexp_samps = mcmc_df['sigma_exp[' + str(ii+1) + ']']

        # sigma_exp
        param_table.loc[param_table['Phase'] == ph, 'Experimental Error Variability'] = np.mean(t_sigexp_samps)

        # medians
        dummy = results_table.loc[results_table['Phase'] == ph,'u_int_count']/results_table.loc[results_table['Phase'] == ph,'R_calc']
        param_table.loc[param_table['Phase'] == ph, 'X-ray Count Variability'] = np.median(dummy)

        dummy = results_table.loc[results_table['Phase'] == ph,'u_int_fit']/results_table.loc[results_table['Phase'] == ph,'R_calc']
        param_table.loc[param_table['Phase'] == ph, 'Parameter Fit Variability'] = np.median(dummy)

        # crystallites diffracted
        dummy = results_table.loc[results_table['Phase'] == ph,'u_cryst_diff']/results_table.loc[results_table['Phase'] == ph,'R_calc']
        param_table.loc[param_table['Phase'] == ph, 'Crystallites Diffracted Variability'] = np.median(dummy)

    if multiple_samples:
        param_table.loc[:,'Sample Variability'] = np.mean(mcmc_df['sigma_sample'])


    return param_table
