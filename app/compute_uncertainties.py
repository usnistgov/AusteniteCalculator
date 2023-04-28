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

def get_unique_phases(results_table):

    intables = list(results_table.values())

    indata = pd.concat(intables,axis=0).reset_index(drop=True)

    return np.unique(indata.Phase)

def concat_results_tables(results_table,from_records=False):

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

    indata = concat_results_tables(results_table)

    mydf = pd.DataFrame({
        'I':indata.int_fit,
        'R':indata.R_calc,
        'sigma_I':indata.u_int_fit,
        'u_int_count':indata.u_int_count,
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

    # compute prior scales
    if  len(results_table) > 1:
        prior_sample_scale = np.mean(mydf.groupby(['sample_id','phase_id']).mean().IR.groupby('phase_id').std())

    else:
        prior_sample_scale = None

    prior_exp_scale = np.mean(mydf.groupby(['sample_id','phase_id']).std().IR)
    prior_location = np.array(mydf.groupby('phase_id').mean().IR)

    print("Prior sample scale: {}".format(prior_sample_scale))
    print("Prior exp scale: {}".format(prior_exp_scale))
    print("Prior location: {}".format(prior_location))
    print("Prior scale: {}".format(np.std(mydf.IR)))

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
        
        
        model = CmdStanModel(stan_file='../stan_files/one_sample.stan')
        #model = CmdStanModel(exe_file=exe_file)

        stan_data = {
            "N":mydf.shape[0],
            "N_phases":len(np.unique(mydf.phases)),
            "Y":mydf.IR,
            "phase":mydf.phase_id,
            "prior_scale":np.std(mydf.IR),
            "prior_exp_scale":prior_exp_scale,
            "prior_location":prior_location,
            "u_int_fit":mydf.sigma_I/mydf.R,
            "u_int_count":mydf.u_int_count/mydf.R
        }



        if fit_variational:
            fit = model.variational(data=stan_data,grad_samples=20,output_samples=2000,require_converged=False)

        else: 
            fit = model.sample(data=stan_data,
                               chains=4,
                               iter_warmup=number_mcmc_runs, 
                               iter_sampling=2000)

        

    # multiple samples
    elif len(results_table) > 1:
  
          #check OS to determine which stan executable to use
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
            "u_int_count":mydf.u_int_count/mydf.R
        }



        if fit_variational:
            fit = model.variational(data=stan_data,grad_samples=20,output_samples=2000,require_converged=False)

        else:
            fit = model.sample(data=stan_data,
                               chains=4,
                               iter_warmup=number_mcmc_runs, 
                               iter_sampling=2000)
    
    if fit_variational:
    
        mcmc_df = pd.DataFrame(fit.variational_sample)
        mcmc_df.columns = fit.variational_params_pd.columns
    

    else:
        mcmc_df = fit.draws_pd()
        print(mcmc_df.info(memory_usage=True))


    mcmc_df.drop(inplace=True,columns = mcmc_df.columns[mcmc_df.columns.str.contains("(__)|(effect)",regex=True)])

    return mcmc_df

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

def generate_pf_plot_and_table(mcmc_df,unique_phase_names,results_table):

    mu_res = np.array(mcmc_df.loc[:,mcmc_df.columns.str.contains('phase_mu')])
    n_phase = mu_res.shape[1]
    multiple_samples = 'sigma_sample' in mcmc_df.columns
    
    row_sums = np.sum(mu_res,axis=1)
    mu_res_norm = mu_res

    for ii in range(n_phase):
        mu_res_norm[:,ii] = mu_res_norm[:,ii]/row_sums
        
    out_df = [None]*n_phase

    quantiles = np.zeros((n_phase,2))

    # table to store phase fraction estimates and 95% credible intervals
    pf_table = pd.DataFrame({
        'Phase':unique_phase_names,
        'Phase Fraction Estimate':0,
        'Phase Fraction (Lower 95%)':0,
        'Phase Fraction (Upper 95%)':0
    })

    # table to hold parameter estimates for sources of uncertainty

    param_table = pd.DataFrame({
        'Phase':unique_phase_names,
        'Experimental Error Variability':[0]*n_phase,
        'X-ray Count Median Variability':[0]*n_phase,
        'Parameter Fit Median Variability':[0]*n_phase
    })

    if multiple_samples:
        param_table['sigma_samp'] = [0]*n_phase
        param_table['sigma_interaction'] = [0]*n_phase

    results_table = pd.concat(results_table,axis=0).reset_index()
    results_table = results_table.loc[results_table['Peak_Fit_Success'],:]


    for ii,ph in enumerate(unique_phase_names):

        out_df[ii] = pd.DataFrame({
            'mu_samps':mu_res_norm[:,ii],
            'phase':unique_phase_names[ii]
        })

        quantiles[ii,:] = np.quantile(mu_res_norm[:,ii],(.025,.975))
        
        #t_mu_samps = mcmc_df['phase_mu[' + str(ii+1) + ']']
        t_sigexp_samps = mcmc_df['sigma_exp[' + str(ii+1) + ']']
        
        pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction Estimate'] = np.mean(mu_res_norm[:,ii])
        pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction (Lower 95%)'] = np.quantile(mu_res_norm[:,ii],.025)
        pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction (Upper 95%)'] = np.quantile(mu_res_norm[:,ii],.975)

        # sigma_exp
        param_table.loc[param_table['Phase'] == ph, 'Experimental Error Variability'] = np.mean(t_sigexp_samps)

        # medians
        dummy = results_table.loc[results_table['Phase'] == ph,'u_int_count']/results_table.loc[results_table['Phase'] == ph,'R_calc']
        param_table.loc[param_table['Phase'] == ph, 'X-ray Count Variability'] = np.median(dummy)

        dummy = results_table.loc[results_table['Phase'] == ph,'u_int_fit']/results_table.loc[results_table['Phase'] == ph,'R_calc']
        param_table.loc[param_table['Phase'] == ph, 'Parameter Fit Variability'] = np.median(dummy)
    
    if multiple_samples:
        param_table.loc[:,'sigma_samp'] = np.mean(mcmc_df['sigma_sample'])
        param_table.loc[:,'sigma_interaction'] = np.mean(mcmc_df['sigma_interaction'])
        param_table['Sample Variability'] = np.sqrt( param_table['sigma_samp']**2 + param_table['sigma_interaction']**2)
        param_table = param_table.drop(columns=['sigma_samp','sigma_interaction'])



    out_df = pd.concat(out_df,axis=0).reset_index(drop=True)
    
    quantiles = quantiles.flatten()

    col_list = px.colors.qualitative.Plotly
    
    # figure
    fig = px.histogram(out_df,x='mu_samps',color='phase',opacity=.75,barmode="overlay")
    
    for ii in range(len(quantiles)):
        fig.add_vline(quantiles[ii],opacity=.5,line_dash='dash',line_color=col_list[ ii // 2 ])

    return fig, pf_table, param_table

def generate_pf_table(mcmc_df,unique_phase_names):

    mu_res = np.array(mcmc_df.loc[:,mcmc_df.columns.str.contains('phase_mu')])
    n_phase = mu_res.shape[1]
    
    row_sums = np.sum(mu_res,axis=1)
    mu_res_norm = mu_res

    for ii in range(n_phase):
        mu_res_norm[:,ii] = mu_res_norm[:,ii]/row_sums
        
    out_df = [None]*n_phase

    quantiles = np.zeros((n_phase,2))

    # table to store phase fraction estimates and 95% credible intervals
    pf_table = pd.DataFrame({
        'Phase':unique_phase_names,
        'Phase Fraction Estimate':0,
        'Phase Fraction (Lower 95%)':0,
        'Phase Fraction (Upper 95%)':0
    })

    for ii,ph in enumerate(unique_phase_names):

        out_df[ii] = pd.DataFrame({
            'mu_samps':mu_res_norm[:,ii],
            'phase':unique_phase_names[ii]
        })

        quantiles[ii,:] = np.quantile(mu_res_norm[:,ii],(.025,.975))
        
        pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction Estimate'] = np.mean(mu_res_norm[:,ii])
        pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction (Lower 95%)'] = np.quantile(mu_res_norm[:,ii],.025)
        pf_table.loc[pf_table['Phase'] == ph,'Phase Fraction (Upper 95%)'] = np.quantile(mu_res_norm[:,ii],.975)

    return pf_table

def generate_param_table(mcmc_df,unique_phase_names,results_table):

    mu_res = np.array(mcmc_df.loc[:,mcmc_df.columns.str.contains('phase_mu')])
    n_phase = mu_res.shape[1]
    multiple_samples = 'sigma_sample' in mcmc_df.columns
    
    # table to hold parameter estimates for sources of uncertainty
    param_table = pd.DataFrame({
        'Phase':unique_phase_names,
        'Experimental Error Variability':[0]*n_phase,
        'X-ray Count Variability':[0]*n_phase,
        'Parameter Fit Variability':[0]*n_phase
    })

    if multiple_samples:
        param_table['Sample Variability'] = [0]*n_phase

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
    
    if multiple_samples:
        param_table.loc[:,'Sample Variability'] = np.mean(mcmc_df['sigma_sample'])


    return param_table

def generate_pf_plot(mcmc_df,unique_phase_names):

    mu_res = np.array(mcmc_df.loc[:,mcmc_df.columns.str.contains('phase_mu')])
    n_phase = mu_res.shape[1]
    
    row_sums = np.sum(mu_res,axis=1)
    mu_res_norm = mu_res

    for ii in range(n_phase):
        mu_res_norm[:,ii] = mu_res_norm[:,ii]/row_sums
        
    out_df = [None]*n_phase
    quantiles = np.zeros((n_phase,2))


    for ii,ph in enumerate(unique_phase_names):

        out_df[ii] = pd.DataFrame({
            'mu_samps':mu_res_norm[:,ii],
            'phase':ph
        })

        quantiles[ii,:] = np.quantile(mu_res_norm[:,ii],(.025,.975))

    out_df = pd.concat(out_df,axis=0).reset_index(drop=True)
    
    quantiles = quantiles.flatten()

    col_list = px.colors.qualitative.Plotly
    
    # figure
    fig = px.histogram(out_df,x='mu_samps',color='phase',opacity=.75,labels={'mu_samps': "Phase Fraction",'phase':"Phase"},histnorm='probability',nbins=100,range_x=[0,1],barmode='overlay')
    
    for ii in range(len(quantiles)):
        fig.add_vline(quantiles[ii],opacity=.5,line_dash='dash',line_color=col_list[ ii // 2 ])

    return fig

