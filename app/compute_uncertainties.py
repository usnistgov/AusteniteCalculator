from enum import unique
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from scipy.stats import truncnorm
from cmdstanpy import CmdStanModel
import sys

def gen_mu_sigma(x,n_draws):
    
    # p(mu,simga) \prop_to 1/sigma OR uniform prior on mu, log(sigma)
    # BDA pg: 66

    # input: x is a 1d array object
    # returns: posterior samples of mu and sigma in a dictionary
    
    x_var = np.var(x)
    n_x = x.shape[0]
    v = n_x-1
    tau2 = x_var
    
    sigma2 = invgamma.rvs(a=v/2,scale=v*tau2/2,size=n_draws)
    mu = t.rvs(df=n_x-1, loc=np.mean(x), scale=np.sqrt(x_var/n_x), size=n_draws)
    
    return {'mu':mu, 'sigma2':sigma2}
    
def get_posterior_samples_cp(I,R,sigma_I,phases,n_draws):

    I = np.array(I)
    R = np.array(R)
    sigma_I = np.array(sigma_I)
    phases = np.array(phases)

    Z = I/R
    unique_phase_names = np.unique(phases)

    res_dict = {}

    for ii in range(len(unique_phase_names)):

        res_dict[unique_phase_names[ii]] = gen_mu_sigma(Z[phases==unique_phase_names[ii]],n_draws)

    return res_dict


def run_paul_mandel(results_table):

    intables = list(results_table.values())

    # create numeric sample ids
    for ii, val in enumerate(intables): 
        intables[ii] = intables[ii].loc[intables[ii]['Peak_Fit_Success'],:]
        intables[ii]['sample_id'] = ii+1

    indata = pd.concat(intables,axis=0).reset_index(drop=True)

    mydf = pd.DataFrame({
        'I':indata.int_fit,
        'R':indata.R_calc,
        'sigma_I':indata.u_int_fit,
        'phases':indata.Phase,
        'two_th':indata.two_theta,
        'sample_id':indata.sample_id
    })


    # create numeric phase id's
    mydf['phase_id'] = 0
    unique_phases = np.unique(mydf.phases)

    for ii, pn in enumerate(unique_phases):
        mydf.loc[mydf['phases'] == pn,'phase_id'] = ii+1

    # compute normalized intensities
    mydf['IR'] = mydf.I / mydf.R
    mydf['sig_IR'] = mydf['sigma_I']/mydf.R
    # unceratinty from fitting and from poisson noise
    # the sqrt(x)**2 is redundant but shows thought process
    sigma_Z = np.sqrt(sigma_I**2 + np.sqrt(I)**2)/R 
    unique_phase_names = np.unique(phase_names)

    summary_table = pd.DataFrame({
        'phase':unique_phase_names,
        'PF_Est':np.zeros(len(unique_phase_names)),
        'PF_L95':np.zeros(len(unique_phase_names)),
        'PF_U95':np.zeros(len(unique_phase_names)),
        'tau_est':np.zeros(len(unique_phase_names)),
        'med_sigma_Z_fit':np.zeros(len(unique_phase_names)),
        'med_sigma_Z_count':np.zeros(len(unique_phase_names))
    })

    tau_ests = np.zeros(len(unique_phase_names))

    mu_dfs = [None]*len(unique_phase_names) # list of dataframes 
    mu_samps_acc = np.zeros(n_draws) # accumulating sum for later normalization

    for ii in range(len(unique_phase_names)):

        inds = phases==unique_phase_names[ii]
        res = combine_effects(Z[inds],sigma_Z[inds]**2,method_re='iterated').summary_frame()
        # simulate samples from approximate 'posterior'
        mu_samps = truncnorm.rvs(0, np.Inf,loc=res.loc['random effect','eff'],scale=res.loc['random effect','sd_eff'], size=n_draws)
        mu_dfs[ii] = pd.DataFrame({
            'which_phase':unique_phase_names[ii],
            'value':mu_samps
        })
        mu_samps_acc = mu_samps_acc + mu_samps

        tau_ests[ii], c = _fit_tau_iterative(Z[inds],sigma_Z[inds]**2)
        summary_table.loc[summary_table.phase == unique_phase_names[ii],'tau_est'] = np.sqrt(tau_ests[ii])
        summary_table.loc[summary_table.phase == unique_phase_names[ii],'med_sigma_Z_fit'] = np.median(sigma_I[inds]/R[inds])
        summary_table.loc[summary_table.phase == unique_phase_names[ii],'med_sigma_Z_count'] = np.median(np.sqrt(I[inds])/R[inds])

    for ii in range(len(unique_phase_names)):
        mu_dfs[ii]['value'] = mu_dfs[ii]['value'] / mu_samps_acc
        quantiles = np.quantile(mu_dfs[ii]['value'],[.5,.025,.975])
        summary_table.loc[summary_table['phase'] == unique_phase_names[ii],['PF_Est','PF_L95','PF_U95']] = quantiles

    summary_table = pd.DataFrame(summary_table)
    
    return {'mu_df':mu_dfs,
            'unique_phase_names':unique_phase_names,
            'summary_table':summary_table}

def run_stan(results_table):

    intables = list(results_table.values())

    # create numeric sample ids
    for ii, val in enumerate(intables): 
        intables[ii] = intables[ii].loc[intables[ii]['Peak_Fit_Success'],:]
        intables[ii]['sample_id'] = ii+1

    indata = pd.concat(intables,axis=0).reset_index(drop=True)

    mydf = pd.DataFrame({
        'I':indata.int_fit,
        'R':indata.R_calc,
        'sigma_I':indata.u_int_fit,
        'phases':indata.Phase,
        'two_th':indata.two_theta,
        'sample_id':indata.sample_id
    })

    # create numeric phase id's
    mydf['phase_id'] = 0
    unique_phases = np.unique(mydf.phases)

    for ii, pn in enumerate(unique_phases):
        mydf.loc[mydf['phases'] == pn,'phase_id'] = ii+1

    # compute normalized intensities
    mydf['IR'] = mydf.I / mydf.R
    mydf['sig_IR'] = mydf['sigma_I']/mydf.R

    # sigle sample
    if len(results_table) == 1:

        # stan
        
        #check OS to determine which stan executable to use
        # Should this be a try/except block?   https://stackoverflow.com/questions/17322208/multiple-try-codes-in-one-block
        if sys.platform.startswith('win'): #windows
            #Untested
            exe_file = '../stan_files/one_sample.exe'
        elif sys.platform.startswith('darwin'): # MacOS
            exe_file = '../stan_files/one_sample'
        elif sys.platform.startswith('linux'):
            # Untested.  If we include precompiled files, we may need to change the filename
            exe_file = '../stan_files/one_sample'
        else:
            print("Not a recognized OS")
        
        
        model = CmdStanModel(exe_file=exe_file)

        stan_data = {
            "N":mydf.shape[0],
            "N_phases":len(np.unique(mydf.phases)),
            "Y":mydf.IR,
            "phase":mydf.phase_id,
            "prior_scale":np.std(mydf.IR),
            "prior_location":np.mean(mydf.IR)
        }

        fit = model.sample(data=stan_data,
                           chains=4,
                           iter_warmup=2000, 
                           iter_sampling=2000)

    # multiple samples
    elif len(results_table) > 1:
    
        exe_file = '../stan_files/multiple_samples.exe'
        model = CmdStanModel(exe_file=exe_file)

        stan_data = {
            "N":mydf.shape[0],
            "N_samples":len(np.unique(mydf.sample_id)),
            "N_phases":len(np.unique(mydf.phases)),
            "Y":mydf.IR,
            "phase":mydf.phase_id,
            "group":mydf.sample_id,
            "prior_scale":np.std(mydf.IR),
            "prior_location":np.mean(mydf.IR)
        }

        fit = model.sample(data=stan_data,
                           chains=4,
                           iter_warmup=2000, 
                           iter_sampling=2000)

    return fit, unique_phases

def run_mcmc(I,R,sigma_I,phases,pfs,plot=False):
    # uses pymc3

    I = np.array(I)[pfs]
    R = np.array(R)[pfs]
    sigma_I = np.array(sigma_I)[pfs]
    phases = np.array(phases)[pfs]


    phase_counts = np.unique(phases, return_counts=True)[1]

    if np.min(phase_counts) <= 2:
        return None

    phase_names = phases.copy()

    Z = I/R
    unique_phase_names = np.unique(phase_names)

    phases = np.zeros(len(phases),dtype=np.int8)
    
    # create numeric index for each phase
    for ii in range(len(unique_phase_names)):

        phases[phase_names==unique_phase_names[ii]] = int(ii)

    unique_phases = np.unique(phases)
    phase_stds = np.zeros(len(unique_phases))

    # standard deviations for each phase
    for ii in range(len(unique_phases)):

        phase_stds[ii] = np.std(Z[phases==unique_phases[ii]])

    # prior scale and means
    prior_scale=np.mean(phase_stds)
    prior_mean_centers = np.ones(len(unique_phases))

    #print(prior_scale)
    #print(prior_mean_centers)   

    if plot:
        plt.scatter(x=np.arange(len(Z)),y=Z,c=phases)
        print("Z: {}".format(Z))
        print("phases: {}".format(phases))

    basic_model = pm.Model() 

    with basic_model:
        
        # Priors for unknown model parameters
        sigma_exp = pm.HalfStudentT("sigma_exp", sd=prior_scale*2, nu=4,shape=len(unique_phases))
        mu = pm.TruncatedNormal("mu", 
                       mu=prior_mean_centers, 
                       sd=np.std(Z)*10,
                       lower=0,
                       shape=len(unique_phases))
        
        full_sigma = pm.math.sqrt( (1/R**2)*(sigma_I**2) + pm.math.sqr(sigma_exp[phases]) )

        # Likelihood (sampling distribution) of observations
        Y_obs = pm.Normal("Y_obs", mu=mu[phases], sd=full_sigma, observed=Z)

        #if plot:
            #pm.model_to_graphviz(basic_model)

        trace = pm.sample(1000, return_inferencedata=False,tune=1000)
        
        mu_norm = np.apply_along_axis(lambda x: x/np.sum(x),1,trace['mu'])
        
        mu_df = pd.DataFrame(mu_norm,columns=unique_phase_names)
        mu_df = pd.melt(mu_df,value_vars = unique_phase_names,var_name='which_phase',value_name='value')
        
        #sig_df = pd.DataFrame(trace['sigma_exp'],columns=unique_phase_names)
        #sig_df = pd.melt(sig_df,value_vars = unique_phase_names,var_name='which_phase',value_name='value')

    summary_table = pd.DataFrame({
        'phase':unique_phase_names,
        'PF_Est':np.zeros(len(unique_phase_names)),
        'PF_L95':np.zeros(len(unique_phase_names)),
        'PF_U95':np.zeros(len(unique_phase_names))
    })

    for ii, pn in enumerate(unique_phase_names):

        quantiles = np.quantile(mu_df['value'].loc[mu_df['which_phase']==pn],[.5,.025,.975])
        summary_table.loc[summary_table['phase'] == pn, ['PF_Est','PF_L95','PF_U95']] = quantiles

    return {'mu_df':mu_df,'trace':trace,
            'unique_phase_names':unique_phase_names,
            'summary_table':summary_table}


def generate_pf_plot(fit,unique_phase_names):
    # fit from model.sample() in cmdstanpy
    mcmc_df = fit.draws_pd()
    mu_res = np.array(mcmc_df.loc[:,mcmc_df.columns.str.contains('phase_mu')])
    n_phase = mu_res.shape[1]
    
    row_sums = np.sum(mu_res,axis=1)
    mu_res_norm = mu_res

    for ii in range(n_phase):
        mu_res_norm[:,ii] = mu_res_norm[:,ii]/row_sums
        
    out_df = [None]*n_phase

    quantiles = np.zeros((n_phase,2))

    for ii in range(n_phase):

        out_df[ii] = pd.DataFrame({
            'mu_samps':mu_res_norm[:,ii],
            'phase':unique_phase_names[ii]
        })

        quantiles[ii,:] = np.quantile(mu_res_norm[:,ii],(.025,.975))

    out_df = pd.concat(out_df,axis=0).reset_index(drop=True)
    
    quantiles = quantiles.flatten()
    
    fig = px.histogram(out_df,x='mu_samps',color='phase',opacity=.75)
    
    for ii in range(len(quantiles)):
        fig.add_vline(quantiles[ii],opacity=.5,line_dash='dash')
    #fig.show()
    
    return fig
