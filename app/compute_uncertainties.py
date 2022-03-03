from math import trunc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import truncnorm

def compute_pf(samp,phases,unique_phases):

    pf = np.zeros(len(unique_phases))

    for ii in range(len(unique_phases)):
        
        pf[ii] = np.mean(samp[np.where(phases==unique_phases[ii]) ])
    
    pf = pf/np.sum(pf)

    return pf


def compute_uncertainties(I,R,I_unc,R_unc,nsim,phases):

    dim = len(I)
    samps = np.zeros( (nsim,dim) )

    unique_phases = np.unique(phases)
    pf_samps = np.zeros( (nsim, len(unique_phases)))

    for ii in range(nsim):

        for jj in range(dim):

            rand_I = truncnorm.rvs(a=0,b=np.Inf,loc=I[jj],scale=I_unc[jj])
            rand_R = truncnorm.rvs(a=0,b=np.Inf,loc=R[jj],scale=R_unc[jj])
            samps[ii,jj] = rand_I/rand_R

        pf_samps[ii,:] = compute_pf(samps[ii,:],phases,unique_phases)

    return pd.DataFrame({
        'Phase':unique_phases,
        'PF_mean':np.apply_along_axis(np.mean,0,pf_samps),
        'PF_sd':np.apply_along_axis(np.std,0,pf_samps)
    })


if __name__ == '__main__':

    res = compute_uncertainties(I=np.array([2,3,4,5]),
                                R=np.array([1,2,3,5]),
                                I_unc=np.array([.5,.5,.5,.5]),
                                R_unc=np.array([0,0,0,0]),
                                nsim=1000,
                                phases=np.array(['a','c','c','a']))

    print(res)