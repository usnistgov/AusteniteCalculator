import numpy as np
import pandas as pd
from cmdstanpy import CmdStanModel
import sys
import compute_results



def get_unique_phases(results_table):

    """
    **DEPRICATED?**  Not called in other codes
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
    **DEPRICATED?**  Not called in other codes
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


def run_stan(Submit_dict,sum_checkbox,number_mcmc_runs,fit_variational=False):
    """
    **RENAME**
    Runs an external script using Stan (https://mc-stan.org/) to return estimates of the phase fractions assuming a single uncorrelated data set *(one_sample.stan)*. Calculated based on normalized intensity values. Uses Bayesian priors and data to estimate uncertainties expressed as draws via a posterior distrubtion. "Samples" in this case implies xrd files/scans. Sections describe various steps (and use the same text as comment headers).

    * Loop over each dataset
    * Create MCMC_Calc DataFrame from Merged_Peaks
    * Drop any rows where the fit was not successful
    * Add additional columns to MCMC_Calc DataFrame
    * Compute Bayesian prior distributions
    * Run one_sample.stan
    * Add data to submission
    * Convert results to mass and volume phase fractions
    * Generate output tables

    Parameters:
        Submit_dict (Dictionary): Container for calculation
        sum_checkbox (Boolean): True if the datasets are to be summed together
        number_mcmc_runs (Int): Number of MCMC warmup runs. 
        fit_variational (Boolean):  **Depricated?**


    Returns:
        Submit_dict (Dictionary): Container for calculation. Inside each *"Dataset_<n>"* dictionary, new keys of *"MCMC_Calc"*, *"Stan_Data"*, *"MCMC_Data"*, *"MCMC_Result_Number"*, *"MCMC_Result_Mass"*, *"MCMC_Result_Volume"* are added.

    """

    #### Loop over each dataset
    for dataset in Submit_dict["File_Paths"]["Dataset_name"]:
        dataset_number=dataset.split("_")[1]
        #indata = concat_results_tables(results_table)
        
        #### Create MCMC_Calc DataFrame from Merged_Peaks
        
        #n_u_ is the uncertainty normalized by the I/R (normalized intensity)
        # FIX - add peak fit success
        Submit_dict[dataset]["MCMC_Calc"]=Submit_dict[dataset]["Merged_Peaks"][['int_fit', 'R_TI', 'n_int_fit', 'n_u_int_fit', 'n_u_count_fit','n_u_N_Diffracting_95pct','Phase','pos_fit', 'hkl','Peak_Fit_Success2','pos_TI','n_int_LB'  ]]

        #### Drop any rows where the fit was not successful
        #breakpoint()
        rows_to_drop = Submit_dict[dataset]["MCMC_Calc"][Submit_dict[dataset]["MCMC_Calc"]['Peak_Fit_Success2'] == False]
        # drop in place
        Submit_dict[dataset]["MCMC_Calc"].drop(rows_to_drop.index, inplace=True)

        print("Included in MCMC Calc")
        print(Submit_dict[dataset]["MCMC_Calc"])
        # ADD FLAGS
        Submit_dict[dataset]["Flags"]=compute_results.flag_phase_fraction(rows_to_drop[['Phase','hkl']].to_string(header=False, index=False,index_names=False),np.nan,\
                "MCMC Caculation",\
                "Removed Peaks where fit uncertainty was 10X the median value",\
                "Check fit and signal to noise",\
                DF_to_append=Submit_dict[dataset]["Flags"])

        #### Add additional columns to MCMC_Calc DataFrame

        Submit_dict[dataset]["MCMC_Calc"]['sample_id']=dataset_number
        # create numeric phase id's
        Submit_dict[dataset]["MCMC_Calc"]['phase_id'] = 0
        
        # CHECK - any way the order gets changed in the phases?
        # Can we just use the row as the MCMC id, or do we need the name?
        # also check Submit_dict["Phase_Info"]["Unit_Cell"]['unit_cell_mass_CIF']
        
        #unique_phases = np.unique(Submit_dict[dataset]["MCMC_Calc"]["Phase"])

        #for ii, pn in enumerate(unique_phases):
        #    Submit_dict[dataset]["MCMC_Calc"].loc[Submit_dict[dataset]["MCMC_Calc"]["Phase"] == pn,'phase_id'] = ii+1
        
        unique_phases=[]
        # Read from unit cell list for order
        for index, cif_fname in enumerate(Submit_dict["Phase_Info"]["Unit_Cell"].index):
            cif_name=cif_fname.split('.')[0]
            Submit_dict[dataset]["MCMC_Calc"].loc[Submit_dict[dataset]["MCMC_Calc"]["Phase"] == cif_name,'phase_id'] = index+1
            #print(index, cif_fname)
            #print(cif_name, index+1)
            unique_phases.append(cif_name)

        Submit_dict["Phase_Info"]["Unit_Cell"].index

        #### Compute Bayesian prior distributions
        # prior_sample_scale for variation between multiple xrd scans
        prior_sample_scale = np.std(Submit_dict[dataset]["MCMC_Calc"]["n_int_fit"])

        # prior_exp_scale = variation based on peak to peak variation
        prior_exp_scale = np.mean(Submit_dict[dataset]["MCMC_Calc"].groupby(['sample_id','phase_id'])["n_int_fit"].std())
        
        # prior_location is the inital location (value) of the data
        prior_location = np.array(Submit_dict[dataset]["MCMC_Calc"].groupby('phase_id')["n_int_fit"].mean())

        print("Bayesian Prior Estimates")
        print("Prior sample scale: {}".format(prior_sample_scale))
        print("Prior exp scale: {}".format(prior_exp_scale))
        print("Prior location: {}".format(prior_location))
        print("Prior scale: {}".format(np.std(Submit_dict[dataset]["MCMC_Calc"]["n_int_fit"])))


        #### Run one_sample.stan

        #check OS to determine which stan executable to use
        # CHECK - Should this be a try/except block?   https://stackoverflow.com/questions/17322208/multiple-try-codes-in-one-block
        
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

        # N is the number of peaks being passed
        # Stan does the calculation for each peak (not Monte Carlo)
        
        # phase_mu is a representation of the population of average normalized intensity values caculated for each phase N_phases which comes from the variaition of each peak N [ii in loop]
        
        # CHECK - prior_scale - why std over all data?
        stan_data = {
            "N":Submit_dict[dataset]["MCMC_Calc"].shape[0],
            "N_phases":len(np.unique(Submit_dict[dataset]["MCMC_Calc"]["Phase"])),
            "Y":Submit_dict[dataset]["MCMC_Calc"]["n_int_fit"],
            "phase":Submit_dict[dataset]["MCMC_Calc"]['phase_id'],
            "prior_scale":np.std(Submit_dict[dataset]["MCMC_Calc"]["n_int_fit"]), # standard deveiation
            "prior_exp_scale":prior_exp_scale, # mean of the standard deviations
            "prior_location":prior_location, # mean value
            "u_int_fit":Submit_dict[dataset]["MCMC_Calc"]['n_u_int_fit'],
            "u_int_count":Submit_dict[dataset]["MCMC_Calc"]['n_u_count_fit'],
            "u_cryst_diff":Submit_dict[dataset]["MCMC_Calc"]['n_u_N_Diffracting_95pct']
        }


        # Runs 4*2000 samples anyway, number of mcmc runs is warmup period?
        fit = model.sample(data=stan_data,
                            chains=4,
                            iter_warmup=number_mcmc_runs,
                            iter_sampling=2000)

        print(Submit_dict[dataset]["MCMC_Calc"])
        print(fit)
        #breakpoint()

        #### Add data to submission
        
        Submit_dict[dataset]["Stan_Data"]=stan_data
        Submit_dict[dataset]["MCMC_Data"] = fit.draws_pd()
        print("Raw MCMC fit Data")
        print(Submit_dict[dataset]["MCMC_Data"])
        
        print(Submit_dict[dataset]["MCMC_Data"].info(memory_usage=True))

        #Submit_dict[dataset]["MCMC_Data"].drop(inplace=True,columns = Submit_dict[dataset]["MCMC_Data"].columns[Submit_dict[dataset]["MCMC_Data"].columns.str.contains("(__)|(effect)",regex=True)])

        print("Mean phase_mu")
        print(Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")].mean())

        print("Median phase_mu")
        print(Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")].median())
        
        # FIX - move these to a function?
        # Results as number of unit cells
        phase_cols = Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")]
        
        #### Convert results to mass and volume phase fractions
        
        # phase_mu is in terms of the normalized intensities
        # to convert to a phase fraction, need to sum the normalized intensities
        ni_sum = np.sum(phase_cols,axis=1)
        for i in range(phase_cols.shape[1]):
            phase_cols.iloc[:,i] = phase_cols.iloc[:,i]/ni_sum


        Submit_dict[dataset]["MCMC_Result_Number"] = phase_cols

        # Results as mass of unit cells
        
        
        # extract the phase_mu columns and store
        mass_cols = Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")]
        
        # CHECK - may be fragile to assumed order
        for i in range(mass_cols.shape[1]):
            mass_cols.iloc[:,i] = mass_cols.iloc[:,i]*Submit_dict["Phase_Info"]["Unit_Cell"]['unit_cell_mass_CIF'][i]
        mass_sum = np.sum(mass_cols,axis=1)
        for i in range(mass_cols.shape[1]):
            mass_cols.iloc[:,i] = mass_cols.iloc[:,i]/mass_sum

        Submit_dict[dataset]["MCMC_Result_Mass"] = mass_cols

        # Results as volume of unit cells
        
        volume_cols = Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")]
        
        # CHECK - may be fragile to assumed order
        for i in range(volume_cols.shape[1]):
            volume_cols.iloc[:,i] = volume_cols.iloc[:,i]*Submit_dict["Phase_Info"]["Unit_Cell"]['unit_cell_volume_CIF'][i]
        volume_sum = np.sum(volume_cols,axis=1)
        for i in range(volume_cols.shape[1]):
            volume_cols.iloc[:,i] = volume_cols.iloc[:,i]/volume_sum

        Submit_dict[dataset]["MCMC_Result_Volume"] = volume_cols

        print("MCMC Fit data after data reduction")
        print(Submit_dict[dataset]["MCMC_Result_Number"])
        print(Submit_dict[dataset]["MCMC_Result_Mass"])
        print(Submit_dict[dataset]["MCMC_Result_Volume"])

        #Submit_dict[dataset]["MCMC_Data"]=compute_conversion_mcmc_dfs2(Submit_dict[dataset]["MCMC_Data"])

        #breakpoint()
        # FIX - ADD Phase parameter table here?
        
        #### Generate output tables
        
        Submit_dict = generate_param_table(Submit_dict,dataset,unique_phases)
        Submit_dict = generate_pf_table(Submit_dict,dataset,unique_phases)


    return Submit_dict




def run_stan_multi(Submit_dict,sum_checkbox,number_mcmc_runs,fit_variational=False):
    """
    **RENAME**
    Runs an external script using Stan (https://mc-stan.org/) to return estimates of the phase fractions assuming a series of correlated data sets *(multiple_samples.stan)*. Datasets have already been collected in *create_multi_dataset*. Calculated based on normalized intensity values. Uses Bayesian priors and data to estimate uncertainties expressed as draws via a posterior distrubtion. "Samples" in this case implies xrd files/scans. Sections describe various steps (and use the same text as comment headers).

    * Create list of unique_phases
    * Run multiple_samples.stan
    * Add data to submission
    * Convert results to mass and volume phase fractions
    * Generate output tables

    Parameters:
        Submit_dict (Dictionary): Container for calculation
        sum_checkbox (Boolean): True if the datasets are to be summed together
        number_mcmc_runs (Int): Number of MCMC warmup runs. 
        fit_variational (Boolean):  **Depricated?**


    Returns:
        Submit_dict (Dictionary): Container for calculation. Inside each *"Dataset_<n>"* dictionary, new keys of  *"Stan_Data"*, *"MCMC_Data"*, *"MCMC_Result_Number"*, *"MCMC_Result_Mass"*, *"MCMC_Result_Volume"* are added.


    """
    
    dataset="Dataset_multi"
    
    #### Create list of unique_phases
    
    unique_phases=[]
    # Read from unit cell list for order
    for index, cif_fname in enumerate(Submit_dict["Phase_Info"]["Unit_Cell"].index):
        cif_name=cif_fname.split('.')[0]
        Submit_dict[dataset]["MCMC_Calc"].loc[Submit_dict[dataset]["MCMC_Calc"]["Phase"] == cif_name,'phase_id'] = index+1
        #print(index, cif_fname)
        #print(cif_name, index+1)
        unique_phases.append(cif_name)
    
    #### Run multiple_samples.stan

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

    model = CmdStanModel(stan_file = '../stan_files/multiple_samples.stan')
    #model = CmdStanModel(exe_file=exe_file)

    fit = model.sample(data=Submit_dict[dataset]["Stan_Data"],
                       chains=4,
                       iter_warmup=number_mcmc_runs,
                       iter_sampling=2000)

    #### Add data to submission
        
    #Submit_dict[dataset]["Stan_Data"]=stan_data
    Submit_dict[dataset]["MCMC_Data"] = fit.draws_pd()
    print("Raw MCMC fit Data")
    print(Submit_dict[dataset]["MCMC_Data"])
 
    print(Submit_dict[dataset]["MCMC_Data"].info(memory_usage=True))

    # Not clear if mean or median should be used
    print("Mean phase_mu")
    print(Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")].mean())

    print("Median phase_mu")
    print(Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")].median())

    print("Mean sigma_sample")
    print(Submit_dict[dataset]["MCMC_Data"]['sigma_sample'].mean())

    print("Median sigma_sample")
    print(Submit_dict[dataset]["MCMC_Data"]['sigma_sample'].median())

    #mcmc_df.drop(inplace=True,columns = mcmc_df.columns[mcmc_df.columns.str.contains("(__)|(effect)",regex=True)])

    #breakpoint()
    
    ## ADD TABLE WITH sample_effects, will need a blank table for single & summed
    
    # Display sample_effect per phase
    
    phase_cols = Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")]

    #### Convert results to mass and volume phase fractions

    ni_sum = np.sum(phase_cols,axis=1)
    for i in range(phase_cols.shape[1]):
        phase_cols.iloc[:,i] = phase_cols.iloc[:,i]/ni_sum

    Submit_dict[dataset]["MCMC_Result_Number"] = phase_cols

    
    # Results as mass of unit cells

    mass_cols = Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")]

    # CHECK - may be fragile to assumed order
    for i in range(mass_cols.shape[1]):
        mass_cols.iloc[:,i] = mass_cols.iloc[:,i]*Submit_dict["Phase_Info"]["Unit_Cell"]['unit_cell_mass_CIF'][i]
    mass_sum = np.sum(mass_cols,axis=1)
    for i in range(mass_cols.shape[1]):
        mass_cols.iloc[:,i] = mass_cols.iloc[:,i]/mass_sum

    Submit_dict[dataset]["MCMC_Result_Mass"] = mass_cols

    # Results as volume of unit cells

    volume_cols = Submit_dict[dataset]["MCMC_Data"].loc[:,Submit_dict[dataset]["MCMC_Data"].columns.str.contains("phase_mu")]

    # CHECK - may be fragile to assumed order
    for i in range(volume_cols.shape[1]):
        volume_cols.iloc[:,i] = volume_cols.iloc[:,i]*Submit_dict["Phase_Info"]["Unit_Cell"]['unit_cell_volume_CIF'][i]
    volume_sum = np.sum(volume_cols,axis=1)
    for i in range(volume_cols.shape[1]):
        volume_cols.iloc[:,i] = volume_cols.iloc[:,i]/volume_sum

    Submit_dict[dataset]["MCMC_Result_Volume"] = volume_cols

    print("MCMC Fit data after data reduction")
    print(Submit_dict[dataset]["MCMC_Result_Number"])
    print(Submit_dict[dataset]["MCMC_Result_Mass"])
    print(Submit_dict[dataset]["MCMC_Result_Volume"])

    #Submit_dict[dataset]["MCMC_Data"]=compute_conversion_mcmc_dfs2(Submit_dict[dataset]["MCMC_Data"])

    #breakpoint()
    # FIX - ADD Phase parameter table here?

    #### Generate output tables

    Submit_dict = generate_param_table(Submit_dict,dataset,unique_phases)
    Submit_dict = generate_pf_table(Submit_dict,dataset,unique_phases)

    return Submit_dict




def generate_pf_table(Submit_dict,dataset,unique_phase_names):
    """
    **RENAME** Create three *DataFrames* with the mean, median, 1 sigma and 2 sigma phase fraction values in terms of the number of unit cells, mass of unit cells, and volume of unit cells.

    Parameters:
        Submit_dict (Dictionary): Container for calculation
        dataset (String): Name for the dataset
        unique_phase_names (List): list of unique CIF file names

    Returns:
        Submit_dict (Dictionary): Container for calculation. Inside each *"Dataset_<n>"* dictionary, new keys of *"Phase_Fraction_Result_Number"*, *"Phase_Fraction_Result_Mass"*, *"Phase_Fraction_Result_Volume"* are added.

    """

    # Number of unit cells
    
    Submit_dict[dataset]["Phase_Fraction_Result_Number"]=pd.DataFrame({"Phase":unique_phase_names,"Neg_2sigma":np.quantile(Submit_dict[dataset]["MCMC_Result_Number"],0.02275,axis=0)})
    Submit_dict[dataset]["Phase_Fraction_Result_Number"]["Neg_1sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Number"],0.1587,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Number"]["Mean"]=np.nanmean(Submit_dict[dataset]["MCMC_Result_Number"],axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Number"]["Pos_1sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Number"],0.8413,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Number"]["Pos_2sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Number"],0.97725,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Number"]["Median"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Number"],.5,axis=0)
   
    # Mass of unit cells


    Submit_dict[dataset]["Phase_Fraction_Result_Mass"]=pd.DataFrame({"Phase":unique_phase_names, "Neg_2sigma":np.quantile(Submit_dict[dataset]["MCMC_Result_Mass"],0.02275,axis=0)})
    Submit_dict[dataset]["Phase_Fraction_Result_Mass"]["Neg_1sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Mass"],0.1587,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Mass"]["Mean"]=np.nanmean(Submit_dict[dataset]["MCMC_Result_Mass"],axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Mass"]["Pos_1sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Mass"],0.8413,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Mass"]["Pos_2sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Mass"],0.97725,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Mass"]["Median"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Mass"],.5,axis=0)
  
    # Volume of unit cells


    Submit_dict[dataset]["Phase_Fraction_Result_Volume"]=pd.DataFrame({"Phase":unique_phase_names,"Neg_2sigma":np.quantile(Submit_dict[dataset]["MCMC_Result_Volume"],0.02275,axis=0)})
    Submit_dict[dataset]["Phase_Fraction_Result_Volume"]["Neg_1sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Volume"],0.1587,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Volume"]["Mean"]=np.nanmean(Submit_dict[dataset]["MCMC_Result_Volume"],axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Volume"]["Pos_1sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Volume"],0.8413,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Volume"]["Pos_2sigma"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Volume"],0.97725,axis=0)
    Submit_dict[dataset]["Phase_Fraction_Result_Volume"]["Median"]=np.quantile(Submit_dict[dataset]["MCMC_Result_Volume"],.5,axis=0)
    

    #Submit_dict[dataset]["MCMC_Result_Number"]
    print(Submit_dict[dataset]["Phase_Fraction_Result_Number"])
    print(Submit_dict[dataset]["Phase_Fraction_Result_Mass"])
    print(Submit_dict[dataset]["Phase_Fraction_Result_Volume"])
    #breakpoint()


    return Submit_dict



def generate_param_table(Submit_dict,dataset,unique_phase_names):
    """
    **RENAME** Create a *DataFrame* summarizing the sources of uncertainty. **ADD LOGIC FOR MULTI DATASETS**.

    Parameters:
        Submit_dict (Dictionary): Container for calculation
        dataset (String): Name for the dataset
        unique_phase_names (List): list of unique CIF file names

    Returns:
        Submit_dict (Dictionary): Container for calculation. Inside each *"Dataset_<n>"* dictionary, a new key of *"Uncert_Source_Summary"* is added.

    """
    #mu_res = np.array(mcmc_df.loc[:,mcmc_df.columns.str.contains('phase_mu')])
    n_phase = len(unique_phase_names)
    
    # FIX for multiple samples
    #multiple_samples = 'sigma_sample' in mcmc_df.columns
    
    # ADD phase_mu

    # table to hold parameter estimates for sources of uncertainty
    # FIX - rename to add note on median value
    # was param_table
    # CHECK renamed to match variable names, maybe better to make
    Submit_dict[dataset]["Uncert_Source_Summary"] = pd.DataFrame({
        'Phase':unique_phase_names,
        'Mean_n_int_fit':np.zeros(n_phase),
        #'Mean_phase_mu':np.zeros(n_phase),  # values are similar, maybe confusing
        'Median_phase_mu':np.zeros(n_phase),
        #'Mean_sigma_exp':np.zeros(n_phase),  # values are similar, maybe confusing
        'Median_sigma_exp':np.zeros(n_phase),
        'Median_n_u_count_fit':np.zeros(n_phase),
        'Median_n_u_int_fit':np.zeros(n_phase),
        'Median_n_u_N_Diffracting_95pct':np.zeros(n_phase)
    })

    if Submit_dict["Phase_Info"]["Calculation_Type"]=="Multi" and dataset=='Dataset_multi':
        Submit_dict[dataset]["Uncert_Source_Summary"]['Median_sigma_sample']=np.zeros(n_phase)
        
        # Resort order
        Submit_dict[dataset]["Uncert_Source_Summary"] = Submit_dict[dataset]["Uncert_Source_Summary"][['Phase', 'Mean_n_int_fit', 'Median_phase_mu', 'Median_sigma_sample', 'Median_sigma_exp', 'Median_n_u_count_fit', 'Median_n_u_int_fit', 'Median_n_u_N_Diffracting_95pct']]

        # HOW to average the sample effect values, since it's a [sample, phase] array

    print(Submit_dict[dataset]["Uncert_Source_Summary"])

    # FIX for multiple samples
    #if multiple_samples:
    #    Submit_dict[dataset]["Uncert_Source_Summary"]['Sample Variability'] = np.zeros(n_phase)

    #results_table = results_table.loc[results_table['Peak_Fit_Success'],:]



    for ii,ph in enumerate(unique_phase_names):
        
        # NEED TO USE THIS LATER


        # mean normalized intensity
        #mean_ph=0
        #subset_table=results_table.loc[:,['Phase','n_int']]
        # need to add 'float' to keep a dataframe from being returned,
        # which breaks the datatype
        
        # fill mean n_int_fit
        Submit_dict[dataset]["Uncert_Source_Summary"]['Mean_n_int_fit'][ii]=float(Submit_dict[dataset]["Merged_Peaks"].loc[Submit_dict[dataset]["Merged_Peaks"]['Phase']==ph,'n_int_fit'].mean())
        
        #mean_ph=float(subset_table.loc[subset_table['Phase']==ph,'n_int'].mean())
        #param_table.loc[param_table['Phase'] == ph, 'Mean Normalized Intensity'] = mean_ph
        
        # Should we add median phase_mu?
        
        #Submit_dict[dataset]["Uncert_Source_Summary"]['Mean_phase_mu'][ii]=float(Submit_dict[dataset]["MCMC_Data"]['phase_mu[' + str(ii+1) + ']'].mean())

        Submit_dict[dataset]["Uncert_Source_Summary"]['Median_phase_mu'][ii]=float(Submit_dict[dataset]["MCMC_Data"]['phase_mu[' + str(ii+1) + ']'].median())
        
        # sigma_exp
        # ADD!
        
        
        #t_sigexp_samps = mcmc_df['sigma_exp[' + str(ii+1) + ']']
        #param_table.loc[param_table['Phase'] == ph, 'Experimental Error Variability'] = np.mean(t_sigexp_samps)
        
        # Not clear if mean or median should be used

        #Submit_dict[dataset]["Uncert_Source_Summary"]['Mean_sigma_exp'][ii]=float(Submit_dict[dataset]["MCMC_Data"]['sigma_exp[' + str(ii+1) + ']'].mean())
        
        #Try as median since it will be less of an outlier
        #RENAME if we keep this
        #Submit_dict[dataset]["Uncert_Source_Summary"]['Mean_sigma_exp'][ii]=float(Submit_dict[dataset]["MCMC_Data"]['sigma_exp[' + str(ii+1) + ']'].mean())

        Submit_dict[dataset]["Uncert_Source_Summary"]['Median_sigma_exp'][ii]=float(Submit_dict[dataset]["MCMC_Data"]['sigma_exp[' + str(ii+1) + ']'].median())



        # median values
        # FIX - these were coded as mean values, why?
        
        # fill median X-ray Count Variability n_u_count_fit
        Submit_dict[dataset]["Uncert_Source_Summary"]['Median_n_u_count_fit'][ii]=float(Submit_dict[dataset]["Merged_Peaks"].loc[Submit_dict[dataset]["Merged_Peaks"]['Phase']==ph,'n_u_count_fit'].median())
        
        #dummy = results_table.loc[results_table['Phase'] == ph,'u_int_count']/results_table.loc[results_table['Phase'] == ph,'R_calc']
        #param_table.loc[param_table['Phase'] == ph, 'X-ray Count Variability'] = np.median(dummy)

        # fill median X-ray Count Variability n_u_count_fit
        # CHECK was Parameter Fit Variability  is that still captured???
        Submit_dict[dataset]["Uncert_Source_Summary"]['Median_n_u_int_fit'][ii]=float(Submit_dict[dataset]["Merged_Peaks"].loc[Submit_dict[dataset]["Merged_Peaks"]['Phase']==ph,'n_u_int_fit'].median())

        #dummy = results_table.loc[results_table['Phase'] == ph,'u_int_fit']/results_table.loc[results_table['Phase'] == ph,'R_calc']
        #param_table.loc[param_table['Phase'] == ph, 'Parameter Fit Variability'] = np.median(dummy)

        # fill median X-ray Count Variability n_u_count_fit
        # CHECK was Parameter Fit Variability  is that still captured???
        Submit_dict[dataset]["Uncert_Source_Summary"]['Median_n_u_N_Diffracting_95pct'][ii]=float(Submit_dict[dataset]["Merged_Peaks"].loc[Submit_dict[dataset]["Merged_Peaks"]['Phase']==ph,'n_u_N_Diffracting_95pct'].median())

        # crystallites diffracted
        #dummy = results_table.loc[results_table['Phase'] == ph,'u_cryst_diff']/results_table.loc[results_table['Phase'] == ph,'R_calc']
        #param_table.loc[param_table['Phase'] == ph, 'Crystallites Diffracted Variability'] = np.median(dummy)

    # FIX for multiple samples
    #if multiple_samples:
    #    param_table.loc[:,'Sample Variability'] = np.mean(mcmc_df['sigma_sample'])
        if Submit_dict["Phase_Info"]["Calculation_Type"]=="Multi" and dataset=='Dataset_multi':
            Submit_dict[dataset]["Uncert_Source_Summary"]['Median_sigma_sample'][ii]=Submit_dict[dataset]["MCMC_Data"]['sigma_sample'].median()
    

    print("Uncertainty Source Summary")
    print(Submit_dict[dataset]["Uncert_Source_Summary"])
    #breakpoint()

    return Submit_dict
