import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def meas_eq(FF,p,LP,M,A,TT,E,v,phase_factor):
    
    R = ((phase_factor*FF)**2*p*LP*np.exp(-2*M)*A*TT*E)/(v**2)

    return R


def compute_uncertainties(uncertainties,meas_eq,n):

    # uncertainties is a pd.DataFrame with columns 'param','mean','sd'

    ncol = uncertainties.shape[0] # parameters
    nrow = n # num sims

    sim_mat = np.random.normal(loc=uncertainties.iloc[:,1].to_numpy().flatten(), 
                               scale=uncertainties.iloc[:,2].to_numpy().flatten(),
                               size=(nrow,ncol))
    

    meas_res = np.zeros(n)
    
    for ii in range(n):
        meas_res[ii] = meas_eq(*sim_mat[ii,:])

    return meas_res


uncertainties_example = pd.DataFrame({
        'param':['FF','p','LP','M','A','T','E','v','pf'],
        'mean':[14.8,6,8.42,0.02,1,1,1,45.26,4],
        'sd':[.8,0,.5,.002,.05,.05,.05,.002,0]}
    )


# example for single value    

meas_eq(*uncertainties_example.iloc[:,1])

I = 24514.8
unc_res = I/compute_uncertainties(uncertainties_example,meas_eq,1000)

plt.hist(unc_res,bins=20)
plt.axvline(np.quantile(unc_res,[.025]),color='red',linestyle='--')
plt.axvline(np.quantile(unc_res,[.975]),color='red',linestyle='--')
plt.show()

# full example 
data = pd.read_csv('~/Documents/AusteniteCalc/austenitecalculator/ExampleData/DataForNormalizedIntensityCalc.csv')

na_inds = data.loc[:,'Uncer Val'].isna()
data.loc[na_inds,'Uncer Val'] = 0

phases = np.unique(data.loc[:,'Phase'].to_numpy())

nsim = 1000

results = {}

for ii, ph in enumerate(phases):
    
    t_data = data.loc[data.loc[:,'Phase'] == ph,:]
    planes = np.unique(t_data.loc[:,'Plane'].to_numpy())
    
    results[ph] = np.zeros((nsim,len(planes)))

    for jj, pln in enumerate(planes):
        
        t_inds = np.logical_and(data.loc[:,'Phase'] == ph,
                                data.loc[:,'Plane'] == pln)
        
        
        unc_data = data.loc[t_inds,:]
        
        I = unc_data.loc[unc_data.loc[:,'Param'] == 'I','Est Val'].to_numpy()
        
        
        unc_data = unc_data.iloc[1:9,0:3]
        
        if ph == 'Austenite':
            t_pf = 4
            
        elif ph == 'Ferrite':
            t_pf = 2
        
        new_row = pd.DataFrame({'Param':['pf'],'Est Val':[t_pf],'Uncer Val':[0]})
        
        unc_data = pd.concat((unc_data,new_row))

        results[ph][:,jj] = I/compute_uncertainties(unc_data,meas_eq,nsim)

    results[ph] = np.apply_along_axis(np.mean,1,results[ph]).reshape(nsim,1)
    
results = np.concatenate((results['Austenite'],results['Ferrite']),axis=1)
pf_results = np.apply_along_axis(lambda x: x[0]/(x[0] + x[1]),1,results)

plt.hist(pf_results,bins=20)
plt.axvline(np.quantile(pf_results,[.025]),color='red',linestyle='--')
plt.axvline(np.quantile(pf_results,[.975]),color='red',linestyle='--')
plt.show()

