import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#import arviz as az
import pymc3 as pm
from scipy.stats import median_abs_deviation as mad
#from scipy.stats import invgamma, t
from statsmodels.stats.meta_analysis import combine_effects

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


def run_paul_mandel(I,R,sigma_I,phases,pfs,n_draws):

    I = np.array(I)[pfs]
    R = np.array(R)[pfs]
    sigma_I = np.array(sigma_I)[pfs]
    phases = np.array(phases)[pfs]


    phase_counts = np.unique(phases, return_counts=True)[1]

    if np.min(phase_counts) <= 2:
        return None

    phase_names = phases.copy()

    Z = I/R
    sigma_Z = sigma_I/R
    unique_phase_names = np.unique(phase_names)

    mu_dfs = [None]*len(unique_phase_names)
    mu_samps_acc = np.zeros(n_draws)

    for ii in range(len(unique_phase_names)):

        inds = phases==unique_phase_names[ii]
        res = combine_effects(Z[inds],sigma_Z[inds]**2,method_re='iterated').summary_frame()
        mu_samps = np.random.normal(loc=res.loc['random effect','eff'],scale=res.loc['random effect','sd_eff'],size=n_draws)
        mu_dfs[ii] = pd.DataFrame({
            'which_phase':unique_phase_names[ii],
            'value':mu_samps
        })
        mu_samps_acc = mu_samps_acc + mu_samps

    for ii in range(len(unique_phase_names)):
        mu_dfs[ii]['value'] = mu_dfs[ii]['value'] / mu_samps_acc

    return {'mu_df':pd.concat(mu_dfs,axis=0),'unique_phase_names':unique_phase_names}

def run_mcmc(I,R,sigma_I,phases,pfs,plot=False):

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

    return {'mu_df':mu_df,'trace':trace,'unique_phase_names':unique_phase_names}