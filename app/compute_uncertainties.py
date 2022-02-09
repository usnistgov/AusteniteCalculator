from math import trunc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import truncnorm


def compute_uncertainties(I,R,I_unc,R_unc,nsim):

    dim = len(I)
    samps = np.zeros( (nsim,dim) )

    for ii in range(nsim):

        for jj in range(dim):

            rand_I = truncnorm.rvs(a=0,b=np.Inf,loc=I[jj],scale=I_unc[jj])
            rand_R = truncnorm.rvs(a=0,b=np.Inf,loc=R[jj],scale=R_unc[jj])
            samps[ii,jj] = rand_I/rand_R

    mn_ratio = np.apply_along_axis(np.mean,0,samps)
    sd_ratio = np.apply_along_axis(np.std,0,samps)

    out_df = pd.DataFrame({
        'mean':mn_ratio,
        'std_dev':sd_ratio
    })

    return out_df


if __name__ == '__main__':

    res = compute_uncertainties(I=[2,3,4],
                                R=[1,2,3],
                                I_unc=[.5,.5,.5],
                                R_unc=[.5,.5,.5],
                                nsim=1000)

    print(res)