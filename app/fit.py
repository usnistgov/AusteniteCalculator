import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
import json
import os
#from compute_results import flag_phase_fraction
import compute_results

def fit_peaks(hist, peaks_list, Chebyschev_coeffiecients=5):
    """Subroutine to fit data using individual peak fitting

    Args:
        hist: GSAS-II powder diffraciton histogram
        peaks_list: list of 2theta locations to(numpy array)
        Chebyschev_coeffiecients: Number of background parameters (integer)
        
    Returns:

    Raises:

    """
    print("Fitting peaks\n")
    # Set up background refinement
    #? Also maybe belongs in a function
    #? How to adjust the number of background parameters (currently 5)
    hist.set_refinements({'Background': {"no. coeffs": Chebyschev_coeffiecients,'type': 'chebyschev-1', 'refine': True}})
    hist.refine_peaks()

    # Fit all of the peaks in the peak list
    for peak in peaks_list:
        hist.add_peak(1, ttheta=peak)
        
    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    
    #breakpoint()
    
    # First fit only the area
    hist.set_peakFlags(area=True)
    hist.refine_peaks()
            
    # Second, fit the area and position
    hist.set_peakFlags(pos=True,area=True)
    hist.refine_peaks()

    # Third, fit the area, position, and gaussian (sig) component of the width
    hist.set_peakFlags(pos=True,area=True,sig=True)
    hist.refine_peaks()

    # Fourth, fit the area, position, and lortenzian (gam) component of the width, while holding the prior sigma value
    hist.set_peakFlags(pos=True,area=True,sig=False,gam=True)
    hist.refine_peaks(mode = 'hold')

    # Fifth, fit the area, position, and gaussian (sig) component of the width again, while holding the prior gam value
    # otherwise large peaks are missing intensity...
    hist.set_peakFlags(pos=True,area=True,sig=True,gam=False)
    hist.refine_peaks(mode = 'hold')

    # Additional cycles seem to just bounce between values. Ending with a sig fit seems to help get the larger peaks.

    # Fit the area, position, gaussian (sig) and lortenzian (gam) component simultaneously
    # Still tends to be unstable since sig and gam are highly correlate...
    #hist.set_peakFlags(pos=True,area=True,sig=True, gam=True)
    #hist.refine_peaks()


def fit_peaks_LeBail_assist(hist, LeBail_peaks_DF, Chebyschev_coeffiecients=5):
    """Subroutine to fit data using peaks found from LeBail fitting

    Args:
        hist: GSAS-II powder diffraciton histogram
        peaks_list: list of 2theta locations to(numpy array)
        Chebyschev_coeffiecients: Number of background parameters (integer)
        
    Returns:

    Raises:

    """
    
    ## SHOULD EXPORT THE UNCERTAINTIES OR RESET VALUES FOR SIG/GAM
    
    print("Fitting peaks\n")
    # Set up background refinement
    #? Also maybe belongs in a function
    #? How to adjust the number of background parameters (currently 5)
    hist.set_refinements({'Background': {"no. coeffs": Chebyschev_coeffiecients,'type': 'chebyschev-1', 'refine': True}})
    hist.refine_peaks()

    # Add peak location and area
    for i in range(len(LeBail_peaks_DF['pos_LB'])):
        #print(LeBail_peaks_DF['LeBail_Int'][i], LeBail_peaks_DF['pos'][i])
        hist.add_peak(LeBail_peaks_DF['int_LB'][i],ttheta=LeBail_peaks_DF['pos_LB'][i] )
        
    # Zero, Refine with nothing fitting
    hist.set_peakFlags(area=False)
    hist.refine_peaks()

    # First, fit only the sigma (const position and intensity)
    hist.set_peakFlags(sig=True)
    hist.refine_peaks()
    
    # Second, fit only gamma while holding sigma
    hist.set_peakFlags(sig=False,gam=True)
    hist.refine_peaks(mode = 'hold')
            
    # Third, area while holding position
    hist.set_peakFlags(area=True,gam=False)
    hist.refine_peaks(mode = 'hold')

    # Fourth, pos while holding area
    hist.set_peakFlags(pos=True, area=False)
    hist.refine_peaks(mode = 'hold')

    # Fifth, area and sigma
    hist.set_peakFlags(pos=False, area=True, sig=True)
    hist.refine_peaks(mode = 'hold')

    # Sixth, pos and area
    hist.set_peakFlags(pos=True, area=True, sig=False)
    hist.refine_peaks(mode = 'hold')

    # Seventh, pos, area, sigma
    hist.set_peakFlags(pos=True, area=True, sig=True)
    hist.refine_peaks(mode = 'hold')

    # Eigth, try gamma again
    hist.set_peakFlags(pos=False, area=False, sig=False, gam=True)
    hist.refine_peaks(mode = 'hold')

    # Final, just pos and area
    hist.set_peakFlags(pos=True, area=True,sig=False, gam=False)
    hist.refine_peaks(mode = 'hold')


#    # Third, fit the area, position, and gaussian (sig) component of the width
#    hist.set_peakFlags(pos=True,area=True,sig=True)
#    hist.refine_peaks()
#
#    # Fourth, fit the area, position, and lortenzian (gam) component of the width, while holding the prior sigma value
#    hist.set_peakFlags(pos=True,area=True,gam=True)
#
#    # Fifth, fit the area, position, and gaussian (sig) component of the width again, while holding the prior gam value
#    # otherwise large peaks are missing intensity...
#    hist.set_peakFlags(pos=True,area=True,sig=True,gam=False)
#    hist.refine_peaks(mode = 'hold')

    # Additional cycles seem to just bounce between values. Ending with a sig fit seems to help get the larger peaks.

    # Fit the area, position, gaussian (sig) and lortenzian (gam) component simultaneously
    # Still tends to be unstable since sig and gam are highly correlate...
    #hist.set_peakFlags(pos=True,area=True,sig=True, gam=True)
    #hist.refine_peaks()
    print(hist.data['Peak List'])


def fit_moved_left_peaks(hist, peaks_list, peak_verify):
    """Subroutine to fit data using individual fitting, shifting peaks to the left (lower 2-theta)

    Args:
        hist: GSAS-II powder diffraciton histogram
        peaks_list: list of 2theta locations to(numpy array)
        Chebyschev_coeffiecients: Number of background parameters (integer)
        
    Returns:

    Raises:

    """
    for i in range(len(peak_verify)):
        if peak_verify[i] == False:
            peaks_list[i] -= 0.25
    
    # Set up background refinement
    #? Also maybe belongs in a function
    #? How to adjust the number of background parameters (currently 5)
    hist.set_refinements({'Background': {"no. coeffs": 5,'type': 'chebyschev-1', 'refine': True}})
    hist.refine_peaks()

    # Fit all of the peaks in the peak lists
    for peak in peaks_list:
        hist.add_peak(1, ttheta=peak)

    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    temp_list = list()
    for x in range(len(peak_verify)):
        if(not(peak_verify[x])):
            temp_list.append(x)

    # First fit only the area
    hist.set_peakFlags(peaklist = temp_list, area=True)
    hist.refine_peaks(mode = 'hold')
            
    # Second, fit the area and position
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True)
    hist.refine_peaks(mode = 'hold')

    # Third, fit the area, position, and gaussian componenet of the width
    hist.set_peakFlags(pos=True,area=True,sig=True)
    hist.refine_peaks(mode = 'hold')

def fit_moved_right_peaks(hist, peaks_list, peak_verify):
    """Subroutine to fit data using individual peak fitting, shifting peaks to the right (higher 2-theta)

    Args:
        hist: GSAS-II powder diffraciton histogram
        peaks_list: list of 2theta locations to(numpy array)
        Chebyschev_coeffiecients: Number of background parameters (integer)
        
    Returns:

    Raises:

    """
    for i in range(len(peak_verify)):
        if peak_verify[i] == False:
            peaks_list[i] += 0.25
    # Set up background refinement
    #? Also maybe belongs in a function
    #? How to adjust the number of background parameters (currently 5)
    hist.set_refinements({'Background': {"no. coeffs": 5,'type': 'chebyschev-1', 'refine': True}})
    hist.refine_peaks()

    # Fit all of the peaks in the peak list
    for peak in peaks_list:
        hist.add_peak(1, ttheta=peak)

    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    temp_list = list()
    for x in range(len(peak_verify)):
        if(not(peak_verify[x])):
            temp_list.append(x)

    # First fit only the area
    hist.set_peakFlags(peaklist = temp_list, area=True)
    hist.refine_peaks(mode = 'hold')
            
    # Second, fit the area and position
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True)
    hist.refine_peaks(mode = 'hold')

    # Third, fit the area, position, and gaussian componenet of the width
    hist.set_peakFlags(pos=True,area=True,sig=True)
    hist.refine_peaks(mode = 'hold')   

def fit_peaks_holdsig(hist, peaks_list, Chebyschev_coeffiecients, peak_verify):
    """Subroutine to fit data using individual peak fitting, but hold the sigma value

    Args:
        hist: GSAS-II powder diffraciton histogram
        peaks_list: list of 2theta locations to(numpy array)
        Chebyschev_coeffiecients: Number of background parameters (integer)
        
    Returns:

    Raises:

    """
    print("Fitting peaks\n")
    # Set up background refinement
    #? Also maybe belongs in a function
    #? How to adjust the number of background parameters (currently 5)
    hist.set_refinements({'Background': {"no. coeffs": Chebyschev_coeffiecients,'type': 'chebyschev-1', 'refine': True}})
    hist.refine_peaks()

    #print("Assign from peaks_list\n")
    # Fit all of the peaks in the peak list
    for peak in peaks_list:
        hist.add_peak(1, ttheta=peak)
        
    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    temp_list = []
    for x in range(len(peak_verify)):
        if(not(peak_verify[x])):
            temp_list.append(x)

    # First fit only the area
    hist.set_peakFlags(peaklist = temp_list, area=True)
    hist.refine_peaks(mode = 'hold')
            
    # Second, fit the area and position
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True)
    hist.refine_peaks(mode = 'hold')

    # Third, fit the area, position, and gaussian componenet of the width
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True,gam=True)
    hist.refine_peaks(mode = 'hold')

def fit_peaks_holdgam(hist, peaks_list, peak_verify):
    """Subroutine to fit data using individual peak fitting, holding gamma value

    Args:
        hist: GSAS-II powder diffraciton histogram
        peaks_list: list of 2theta locations to(numpy array)
        Chebyschev_coeffiecients: Number of background parameters (integer)
        
    Returns:

    Raises:

    """
    print("Fitting peaks\n")
    # Set up background refinement
    #? Also maybe belongs in a function
    #? How to adjust the number of background parameters (currently 5)
    hist.set_refinements({'Background': {"no. coeffs": Chebyschev_coeffiecients,'type': 'chebyschev-1', 'refine': True}})
    hist.refine_peaks()

    #print("Assign from peaks_list\n")
    # Fit all of the peaks in the peak list
    for peak in peaks_list:
        hist.add_peak(1, ttheta=peak)
    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    temp_list = []
    for x in range(peak_verify):
        if(peak_verify[x]):
            temp_list.append(peaks_list[x])

    # First fit only the area
    hist.set_peakFlags(peaklist = temp_list, area=True)
    hist.refine_peaks(mode = 'hold')
            
    # Second, fit the area and position
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True)
    hist.refine_peaks(mode = 'hold')

    # Third, fit the area, position, and gaussian componenet of the width
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True,sig=True)
    hist.refine_peaks(mode = 'hold')

def fit_instprm_file(hist, peaks_list, Chebyschev_coeffiecients=5):
    """Subroutine to fit data using individual peak fitting

    Args:
        hist: GSAS-II powder diffraciton histogram
        peaks_list: list of 2theta locations to(numpy array)
        Chebyschev_coeffiecients: Number of background parameters (integer)
        
    Returns:

    Raises:

    """
    print("Fitting peaks\n")
    # Set up background refinement
    #? Also maybe belongs in a function
    #? How to adjust the number of background parameters (currently 5)
    hist.set_refinements({'Background': {"no. coeffs": Chebyschev_coeffiecients,'type': 'chebyschev-1', 'refine': True},
                          'Instrument Parameters': ['U', 'V', 'W', 'X', 'Y']})
    hist.refine_peaks()

    #print("Assign from peaks_list\n")
    # Fit all of the peaks in the peak list
    for peak in peaks_list:
        hist.add_peak(1, ttheta=peak)
    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    
    # First fit only the area
    hist.set_peakFlags(area=True)
    hist.refine_peaks()
            
    # Second, fit the area and position
    hist.set_peakFlags(pos=True,area=True)
    hist.refine_peaks()
    
    # Additional cycles seem to just bounce between values. Ending with a sig fit seems to help get the larger peaks.

    # Fit the area, position, gaussian (sig) and lortenzian (gam) component simultaneously
    # Still tends to be unstable since sig and gam are highly correlate...
    #hist.set_peakFlags(pos=True,area=True,sig=True, gam=True)
    #hist.refine_peaks()


def fit_background(DF, hist, peaks_list, sig_width=3):
    """Subroutine to fit background data

    Args:
        DF: Merged datafile to append to
        hist: GSAS-II powder diffraciton histogram
        peaks_list: list of 2theta locations to(numpy array)
        sig_width: number of standard deviations (width) of gaussian fit to use to extract background values. Default is 3 (99.73%)
    Returns:

    Raises:

    """
    back_counts_list=[]
    fit_counts_list=[]
    data_counts_list=[]
    signal_to_noise_list=[]
    
    for peak in hist.data['Peak List']['peaks']:
        # index [0] is the two theta value. index [4] is the sig value. Sigma and gamma seems to be given in milli-degrees
        print(peak)
        print("Range:", peak[0], sig_width*peak[4]/1000, peak[0]-sig_width*peak[4]/1000, peak[0]+sig_width*peak[4]/1000)
        x_min=peak[0]-sig_width*peak[4]/1000
        x_max=peak[0]+sig_width*peak[4]/1000
        
        indexes = [index for index, value in enumerate(hist.data['data'][1][0]) if value > x_min and value < x_max ]

        back_counts=0
        data_counts=0
        fit_counts=0

        for index in indexes:
        
            back_counts=back_counts+hist.data['data'][1][4][index]
            fit_counts=fit_counts+hist.data['data'][1][3][index]
            data_counts=data_counts+hist.data['data'][1][1][index]

        print("Counts: ",back_counts,fit_counts,data_counts,data_counts-back_counts, peak[2]/(data_counts-back_counts) )
        
        print("\n")
        back_counts_list.append(back_counts)
        fit_counts_list.append(fit_counts)
        data_counts_list.append(data_counts)
        try:
            signal_to_noise_list.append(peak[2]/math.sqrt(back_counts+peak[2]))
        except ValueError:
            signal_to_noise_list.append(np.nan)
            print("Value error in signal to noise")
        
    DF['back_int_bound']=back_counts_list
    DF['signal_to_noise']=signal_to_noise_list
    # used as a diagnostic/sanity check, but using the sigma value as boundaries can result in adjacent peaks adding counts
    #DF['int_back_bound']=fit_counts_list
    #DF['total_back_bound']=data_counts_list
    return DF

def create_verify_list(t_pos, t_int, t_sigma, t_gamma):
    """
    CHECK - best structure?
    """
    verify_list = np.empty(t_pos.shape[0])

    max_int = 0
    for x in range(t_pos.shape[0]):
        if(t_int[x] > t_int[max_int]):
            max_int = x
        
        if(t_int[x] < 0):
            verify_list[x] = False
        else:
            verify_list[x] = True
            print("All Intensities Positive")
            
#        if(t_sigma[x] < 0):
#            verify_list[x] = False
#        else:
#            verify_list[x] = True
#            print("All Sigma Values Positive")
#
#        if(t_gamma[x] < 0):
#            verify_list[x] = False
#        else:
#            verify_list[x] = True
#            print("All Gamma Values Positive")

#    temp_sig = []
 #   temp_gam = []
  #  temp_pos_sig = []
   # temp_pos_gam = []
    #for x in range(t_pos.shape[0]):
     #   if(t_sigma[x] > 0):
      #      temp_sig.append(t_sigma[x])
       #     temp_pos_sig.append(t_pos[x])
        #if(t_gamma[x] > 0):
         #   temp_gam.append(t_gamma[x])
          #  temp_pos_gam.append(t_pos[x])
    # Check if sig, gam values are reasonable
    # Leading to a number of rejected peaks currently
  #  m, b = np.polyfit(temp_pos_sig, temp_sig, 1)

   # for x in range(t_pos.shape[0]):
    #    if(t_sigma[x] > (m * t_pos[x] + b) + t_sigma[max_int] or t_sigma[x] < (m * t_pos[x] + b) - t_sigma[max_int]):
     #       verify_list[x] = False

    #m, b = np.polyfit(temp_pos_gam, temp_gam, 1)

    #for x in range(t_pos.shape[0]):
     #   if(t_gamma[x] > (m * t_pos[x] + b) + t_gamma[max_int] or t_gamma[x] < (m * t_pos[x] + b) - t_gamma[max_int]):
      #      verify_list[x] = False
    
    #print(verify_list)
    return verify_list

def check_fit_success(Merged_Peaks_DF):
    """
    May be duplicative of create_verify_list, but need to fix fitting loops
    
    """
    #breakpoint()
    
    
    # Check if the fitted intensity uncertinaty is less than 10X the median value
    Merged_Peaks_DF["Peak_Fit_Success2"]=Merged_Peaks_DF['n_u_int_fit'] < 10* np.median(Merged_Peaks_DF['n_u_int_fit'])
    
    return Merged_Peaks_DF


def fit_peaks_Rowles(G2sc,Submit_dict,dataset_string,dataset_index,Chebyschev_coeffiecients=5):

#datadir,workdir,xrdml_fname,instprm_fname,cif_fnames, flags_for_user_DF, Chebyschev_coeffiecients=5


    """Subroutine to fit data using LeBail fitting
    Uses suggested order from Matthew Rowles (model 3), arXiv:2008.11046v4
    Also uses full pattern fitting for lattice parameters

    Model 3 Fit order
    0) Set max cycles = 10
    1) bkg sc - background parameters and histogram scale factor
    2) cell - unit cell parameters
    3) ZE SD - Zero error and specimen displacement (correlated?)
    -> Add phase fraction here (with restraint?)
    4) csL - Lorentzian crystal size (can't do these separately in GSAS-II)
    5) PD - packing density (n/a in GSAS-II)
    6) strG - Gaussian microstrain  (Microstrain might be better to fit first)
    7) csG strL - Gaussian crystal size and Lorentzian microstrain
    8) B - Atomic displacement parameter (Uiso in GSAS-II, likely can't change all atoms at once)
    9) All - Fit all simultaneously

    ??? Should I add a parameter for texture to improve fit quality?
    
    ??? Where should phase fraction be refined?
    

    Args:
        GSAS_projfile: GSAS-II project file with histogram
        peaks_list: list of 2theta locations to(numpy array)
        Chebyschev_coeffiecients: Number of background parameters (integer)
        DF_flags: notes to the users
    Returns:

    Raises:

    """
    
    datadir=Submit_dict["File_Paths"]["Data_Directory"]
    workdir=Submit_dict["File_Paths"]["Working_Directory"]
    
    xrdml_fname=Submit_dict["File_Paths"]["Diffraction_Filenames"][dataset_index]
    instprm_fname=Submit_dict["File_Paths"]["Instrument_Filename"]
    cif_fnames=Submit_dict["File_Paths"]["Cif_Filenames"]
    json_data=Submit_dict["Phase_Info"]["Interaction_Parameters"]
    
    
    #data_path_wrap = lambda fil: datadir + '/' + fil
    #save_wrap = lambda fil: workdir + '/' + fil
    
    print("Fitting entire pattern\n")
    
    # Create a new project to avoid collision
    gpx = G2sc.G2Project(newgpx=os.path.join(workdir,'LeBail_fit.gpx'))
    

    
    # Read in phases
    for phase_file in cif_fnames:
        gpx.add_phase(os.path.join(datadir,phase_file),fmthint='CIF') # add a phase to the project
    
    # Read in histogram
    hist = gpx.add_powder_histogram(os.path.join(datadir,xrdml_fname),
                                    os.path.join(datadir,instprm_fname),
                                    phases=gpx.phases(),databank=1, instbank=1)

#    print("Histograms List: ")
#    for i in gpx.histograms():
#        print("Histogram Name: ", i.name)

    ## NEED TO ADD PHASES TO GPX, better to do then add histogram
    # otherwise:
    #print("Link phases")
    #for histogram in gpx.histograms():
    #    for phase in gpx.phases():
    #        gpx.link_histogram_phase(histogram, phase)
    

    # Read sample displacement from data
    # Also could consider setting the number of background coefficients this way
    sample_displacement = json_data['sample_displacement']
  
    ##### Step 0: Set for up to 10 refinement cycles
    gpx.set_Controls('cycles',10)
  
    ##### Step 1: refine the background (and scale, which is enabled by default)
    background_refine={'set': {"Background": {"no. coeffs": Chebyschev_coeffiecients,
                                     'type': 'chebyschev-1', 'refine': True}}}
    gpx.do_refinements([background_refine])
    

    ##### Step 2: enter a value for sample displacement (shift), refine unit cells, scale, and sample displacement
    
    # Shift seems to behave differently than other fitting paramters, hard to set otherwise
    hist.data["Sample Parameters"]['Shift']=[sample_displacement , True]

    # seems like the clear is needed, the refine doesn't seem to take effect
    unitcell_refine={'clear': {"Background": {'refine': False}},
                     'set': {'Sample Parameters': ['Scale'] },
                     'set': {'Cell': True }}

    gpx.do_refinements([unitcell_refine])

    ##### Step 3: use LeBail to extract intensities.  Still refine unit cells
    
    fit_sample_displacement=hist.data["Sample Parameters"]['Shift'][0]
    hist.data["Sample Parameters"]['Shift']=[fit_sample_displacement , False]

    LeBail_refine={'clear': {'Sample Parameters': ['Scale'] },
                   'set': { "LeBail": True}}

    gpx.do_refinements([LeBail_refine])
    
    ##### Step 4: Refine microstrain, still with Le Bail and unit cells
    
    ## Again, the Microstrain seems to be hard to set directly
    print("Setting the HAP strain values")
    for phase in gpx.phases():
        phase.data['Histograms']['PWDR '+xrdml_fname]['Mustrain'][2]=[True, False, False]
        print(phase.data['Histograms']['PWDR '+xrdml_fname]['Mustrain'])
    print()

    # empty set since we did not create a dictionary and modified directly
    gpx.do_refinements()
    
    ##### Step 5 Final refinement, refine displacement, background, unit cell, microstrain
    
    fit_sample_displacement=hist.data["Sample Parameters"]['Shift'][0]
    hist.data["Sample Parameters"]['Shift']=[fit_sample_displacement , True]

    Final_refine={'set': {"Background": {'refine': True}}}

    gpx.do_refinements([Final_refine])
    
    #### Output
    print("Histograms data: ")
    for i in gpx.histograms():
        #print("Histogram data: ", i.data)
        print("Reflection List data: ", i.data.keys())
        for n, phase in  enumerate(gpx.phases()):
            print("Phase name: ",phase.name)
            print("\n\nReflection List data: ", i.data["Reflection Lists"][phase.name]["RefList"])
            # Create a new data frame if it's the first phase
            if n==0:
                LeBail_reflist_DF=pd.DataFrame(i.data["Reflection Lists"][phase.name]["RefList"],
                 columns=['h_LB','k_LB','l_LB','mul_LB','d_LB','pos_LB','sig_LB','gam_LB',
                 'F_obs_sq_LB','F_calc_sq_LB','phase_LB','I_corr_LB','Prfo_LB','Trans_LB','ExtP_LB'])
                LeBail_reflist_DF[['Phase']] = phase.name
                #print(LeBail_reflist_DF)
            # otherwise append
            else:
                LeBail_reflist2_DF=pd.DataFrame(i.data["Reflection Lists"][phase.name]["RefList"],
                 columns=['h_LB','k_LB','l_LB','mul_LB','d_LB','pos_LB','sig_LB','gam_LB',
                 'F_obs_sq_LB','F_calc_sq_LB','phase_LB','I_corr_LB','Prfo_LB','Trans_LB','ExtP_LB'])
                LeBail_reflist2_DF[['Phase']] = phase.name
                LeBail_reflist_DF=pd.concat([LeBail_reflist_DF,LeBail_reflist2_DF],axis=0,ignore_index=True)
                #print(LeBail_reflist_DF)
                #print(LeBail_reflist2_DF)
            
            
            
    LeBail_reflist_DF = LeBail_reflist_DF.sort_values(by='pos_LB')
    LeBail_reflist_DF = LeBail_reflist_DF.reset_index(drop=True)
    # Calculate an intensity
    LeBail_reflist_DF['int_LB']=LeBail_reflist_DF['I_corr_LB']*LeBail_reflist_DF['F_calc_sq_LB']
    # Uncertainties based on sqrt of counts
    LeBail_reflist_DF['u_int_LB']=LeBail_reflist_DF['int_LB']**0.5
    print("Le Bail Reflection List DataFrame")
    print(LeBail_reflist_DF)
    
    
    Submit_dict[dataset_string]["Le_Bail_Peaks"]=LeBail_reflist_DF
    

    # Copy the fitted data as well.
    Submit_dict[dataset_string]["Le_Bail_Data"]=hist.data
    
    # Copy the scale value for use in Theoretical Intensity values
    Submit_dict[dataset_string]["Le_Bail_Scale"] = hist.data["Sample Parameters"]['Scale'][0]

    #### Flags
    #breakpoint()

    # Note the sample displacement
    print("Sample Displacement Found")
    Submit_dict[dataset_string]["Flags"]=compute_results.flag_phase_fraction("{:.4f}".format(hist.data["Sample Parameters"]['Shift'][0]),"micrometers", "Le Bail Fit", "A sample displacement (shift) value was fit", "Check goniometer alignment if this value is large", DF_to_append=Submit_dict[dataset_string]["Flags"])
    
    #flags_for_user_DF=compute_results.flag_phase_fraction(np.nan,
    #"Sample Displacement","A sample displacement (shift) value of: "+"{:.4f}".format(hist.data["Sample Parameters"]['Shift'][0])+" um was fit",
    #"Check goniometer alignment if this value is large",
    # DF_to_append=flags_for_user_DF)

    # Note the microstrain?
    # Reflist has things in terms of sig and gam!
    
    ## Save new peak_list
#                    for n, phase in enumerate(Rowles_proj.phases()):
#                    #print("\n\nReflection List data: ", histogram.data["Reflection Lists"][phase.name]["RefList"])
#                    #print(n)
#                    t_peaks[phase.name] = pd.DataFrame(histogram.data["Reflection Lists"][phase.name]["RefList"])
#                    
#                    
    # Just like in Theoretical Intensities, use Fcsq*Icorr for R



    # TO ADD
    # Save new lattice spacing?
#    fit_lattice=[]
#
#    #print("Phase data: ")
#    for i in gpx.phases():
#        #print("Phase data: ", i.data)
#         #print("Unit Cell: ", i.data.keys())
#        fit_lattice.append(i.data["General"]["Cell"][1])
#        #print("Unit Cell: ", i.data["General"]["Cell"][1])
#        #print("Unit Cell Volume: ", i.data["General"]["Cell"][7])

    print(" \n\n End of Rowles \n\n")
    
    # Grab .lst file and parse?  Or add to data package?
    # Also gpx.data() ?
    # In gpx.data(), the WgtFrac is given, parameter 'depSigDict'
    
    
    # Additional parameters to pull out
    # mass, volume
    # messages from the fitting
    # weight fraction, convert?
    # unit cell uncertinty (where?) - > values for A0 are reciprical metric tensors
    #  But calculation doesn't work out as expected...
    
    # Seems like there's also a scaling factor somewhere?
    
    # Save the cif files for reuse?
    
    return(Submit_dict)


# Fit using only gaussians

### Added for phase fraction calculations

import scipy.optimize as opt
import scipy.integrate as sciint
def fit_peaks_Gaussian(Submit_dict,dataset_string,dataset_index):
    '''
    Use a simple gaussian and linear fit to approximate the curves
    Also use the edges of the gaussian to sum the counts with no peak structure assumed
    


    '''

    TwoTheta_plot=[]
    Gaussian_plot=[]
    Submit_dict[dataset_string]["Gaussian_Data"]={}

    Submit_dict[dataset_string]["Gaussian_Peaks"]=Submit_dict[dataset_string]['Le_Bail_Peaks'][['pos_LB','sig_LB','int_LB']]

    pos_G_list=[]
    sig_G_list=[]
    int_G_list=[]
    int_trap_list=[]
    fit_success_G_list=[]
    int_G_total_list=[]
    int_G_bg_list=[]

    for index, pos_value in enumerate(Submit_dict[dataset_string]['Le_Bail_Peaks']['pos_LB']):

        # sigma values are in centi-degrees, so need to divide by 100
        sig_value=Submit_dict[dataset_string]['Le_Bail_Peaks']['sig_LB'].iloc[index]/100
        int_value=Submit_dict[dataset_string]['Le_Bail_Peaks']['int_LB'].iloc[index]
        print(pos_value, sig_value,int_value)
        
        # [1][0] is the position of the two theta values
        data_index=np.searchsorted(Submit_dict[dataset_string]['Le_Bail_Data']['data'][1][0],pos_value)
        # using 3* the sig_value since Le Bail tends to make the window small
        # and to take a larger view for fitting
        # FIX - need a larger value for right window, with the ka1/ka2 split
        # Was 3/4, increased to check fitting
        left_window_index=np.searchsorted(Submit_dict[dataset_string]['Le_Bail_Data']['data'][1][0],pos_value-5*sig_value)
        right_window_index=np.searchsorted(Submit_dict[dataset_string]['Le_Bail_Data']['data'][1][0],pos_value+6*sig_value)
 
        print(left_window_index,data_index,right_window_index)
        
        #FIX - Need a way to mark when there's overlaps between peaks
        
        print(Submit_dict[dataset_string]['Le_Bail_Data']['data'][1][1][left_window_index:right_window_index])
        
        TwoTheta_window=Submit_dict[dataset_string]['Le_Bail_Data']['data'][1][0][left_window_index:right_window_index]
        Intensity_window=Submit_dict[dataset_string]['Le_Bail_Data']['data'][1][1][left_window_index:right_window_index]

        slope_approx=(Intensity_window[-1] - Intensity_window[0])/ (TwoTheta_window[-1]-TwoTheta_window[0])
        intercept_approx=Intensity_window[0]-slope_approx*TwoTheta_window[0]
        
        # Need the sig_value back in centidegrees?
        #scale_value=int_value/(sig_value*100*np.sqrt(2*np.pi))
        
        scale_value=np.max(Intensity_window)-0.5*(Intensity_window[0]+Intensity_window[-1])
        
        initial_guess=[scale_value, pos_value, 2*sig_value,slope_approx,intercept_approx]
        print("Initial Guess: \n", initial_guess)
        
        
        try:
            popt, pcov = opt.curve_fit(gauss, TwoTheta_window,
                               Intensity_window, p0 = initial_guess )
            print("Fitted Values:")
            print(popt,"\n")
            #print(pcov)
            print(np.sqrt(np.diagonal(pcov)))
            print(gauss(TwoTheta_window,popt[0],popt[1],popt[2],popt[3],popt[4]))
            # need to include the x axis
            # Values are off by Factor of 100, others report in centideg
            Integ_fit=sciint.trapz(gauss(TwoTheta_window,popt[0],popt[1],popt[2],popt[3],popt[4]),x=TwoTheta_window)
            Integ_data=sciint.trapz(Intensity_window,x=TwoTheta_window)
            Integ_background=sciint.trapz(background(TwoTheta_window,popt[3],popt[4]),x=TwoTheta_window)
            Integ_peak_fit=Integ_fit-Integ_background
            Integ_peak_data=Integ_data-Integ_background
            
            fit_success_G=True
            print("Integrated Values:")
            print(Integ_fit,Integ_background,Integ_peak_fit)
            print(Integ_data,Integ_background,Integ_peak_data)

            # extend, not append
            TwoTheta_plot.extend(list(TwoTheta_window))
            Gaussian_plot.extend(list(gauss(TwoTheta_window,popt[0],popt[1],popt[2],popt[3],popt[4])))
        except:
            print("Fitting Error at: {:5.2f}".format(initial_guess[1]))
            popt=[np.nan,np.nan,np.nan,np.nan,np.nan]
            Integ_fit=np.nan
            Integ_data=np.nan
            Integ_background=np.nan
            Integ_peak_fit=np.nan
            Integ_peak_data=np.nan
            fit_success_G=False
            TwoTheta_plot.extend([pos_value])
            Gaussian_plot.extend([0])

        pos_G_list.extend([popt[1]])
        # multiply by 100 to make comparible in centi-degrees
        sig_G_list.extend([popt[2]*100])
        int_G_list.extend([Integ_peak_fit*100])
        int_G_total_list.extend([Integ_fit*100])
        int_G_bg_list.extend([Integ_background*100])
        int_trap_list.extend([Integ_peak_data*100])
        fit_success_G_list.extend([fit_success_G])
                             
        # Save the fit values to plot
        print("Compare values: ")
        print(int_value, Integ_peak_fit,Integ_peak_data)
        #Submit_dict[dataset_string][t_peaks]
        print("**************************************\n\n")
        
        # These values aren't really close to the Le Bail data...
    
        # Sorted list needed for plotting?
        #https://www.geeksforgeeks.org/python-sort-list-according-to-other-list-order/
        # Create dictionary to map 'order' to their indices
        #order_dict = {value: index for index, value in enumerate(order)}

        # Sort 'a' based on 'order' using the dictionary
        #sorted_list = sorted(a, key=lambda x: order_dict[x])
        #print(sorted_list)
    

    Submit_dict[dataset_string]["Gaussian_Peaks"]["pos_G"]=pos_G_list
    Submit_dict[dataset_string]["Gaussian_Peaks"]["sig_G"]=sig_G_list
    Submit_dict[dataset_string]["Gaussian_Peaks"]["int_G"]=int_G_list
    Submit_dict[dataset_string]["Gaussian_Peaks"]["int_G_total"]=int_G_total_list
    Submit_dict[dataset_string]["Gaussian_Peaks"]["int_G_bg"]=int_G_bg_list
    Submit_dict[dataset_string]["Gaussian_Peaks"]["int_TR"]=int_trap_list
    Submit_dict[dataset_string]["Gaussian_Peaks"]["fit_success_G"]=fit_success_G_list
    print("\n*************************************")
    print("Gaussian Fit data")
    print(Submit_dict[dataset_string]["Gaussian_Peaks"])
    
    #Submit_dict[dataset_string]["Gaussian_Peaks"]
    Submit_dict[dataset_string]["Gaussian_Data"]['data']=[TwoTheta_plot,Gaussian_plot]
    
    print("Test Export")
    print(TwoTheta_plot)
    print(Gaussian_plot)
#    breakpoint()
#
#    #psi30-phi0
#    peak_list=[["A200",300,[1e7,50.5, .2, -3e4, 5e6],  5, int(10/0.02)  ],
#               ["F200",1000,[1e8,65,  .2, -3e4, 5e6],   5, int(10/0.02)  ],
#               ["A220",1450,[1e7,74.5,.2, -3e4, 5e6], 5, int(10/0.02)  ],
#               ["F211",1900,[1e8,82.5,.2, -3e4, 5e6], 5, int(10/0.02)  ],
#               ["A311",2300,[1e7,90.5,.2, -3e4, 5e6],  5, int(6/0.02)  ],
#               ["A222",2650,[1e7,95.3,.4, -3e4, 5e6],   5, int(3/0.02)  ],
#               ["F220",2700,[2e7,99,  .2, -3e4, 5e6], 5, int(10/0.02)  ],
#               ["F310",3600,[5e8,116, .4, -3e4, 5e6], 5, int(12/0.02)  ]                     ]
#
#
#
#
#    summary_DF=pd.DataFrame(columns=['Peak Name','Position','Fit Int','Data Int','Sigma','Background Int'])
#
#    for i in range(len(peak_list)):
#
#        peak_name=save_name_base+"_"+peak_list[i][0]
#        print("Peak: ", peak_list[i][0])
#        start_x=peak_list[i][1]
#        initial_guess=peak_list[i][2]
#        sigma_stop=peak_list[i][3]
#        window_size=int(peak_list[i][4]*0.02)
#        window=peak_list[i][4]
#
#
#
#    #########
#
#        # restrict data to an angular window (degrees 2 theta)
#        data1D_DF_Deg_Window=data1D_DF.iloc[start_x:(start_x+window)]
#
#        baf.save_1D_plot_scatter(save_dir,(peak_name+"Deg_Win"),data1D_DF_Deg_Window,
#                                title='{} Raw Data, {:d} deg range'.format(peak_name,window_size))
#
#        (popt_Deg_Window, pcov_Deg_Window)=baf.fit_gauss(data1D_DF_Deg_Window, initial_guess)
#
#        baf.save_1D_plot_fit(save_dir,(peak_name+"Deg_Win"),data1D_DF_Deg_Window, popt_Deg_Window,
#                                title='{}Gaussian fit, {:d} deg range'.format(peak_name,window_size))
#
#        #breakpoint()
#
#        # restrict data further to a window bounded by Gaussian width
#
#        Sig_Window=np.where(np.logical_and(data1D_DF["Two Theta"]>=popt_Deg_Window[1]-sigma_stop*popt_Deg_Window[2],data1D_DF["Two Theta"]<=popt_Deg_Window[1]+sigma_stop*popt_Deg_Window[2]))
#
#        data1D_DF_Sig_Window=data1D_DF.iloc[Sig_Window]
#
#        baf.save_1D_plot_scatter(save_dir,(peak_name+"Sig_Win"),data1D_DF_Sig_Window,
#                                title='{} Raw Data, {:d} sig range'.format(peak_name,sigma_stop))
#
#        #print("Sigma Window: \n", Sig_Window)
#
#        (popt_Sig_Window, pcov_Sig_Window)=baf.fit_gauss(data1D_DF_Sig_Window, popt_Deg_Window)
#
#        baf.save_1D_plot_fit(save_dir,(peak_name+"Sig_Win"),data1D_DF_Sig_Window, popt_Sig_Window,
#                                title='{} Gaussian fit, {:d} sig range'.format(peak_name,sigma_stop))
#
#        # Only pick the left and right bounds
#
#        Sig_Left_Window=np.where(np.logical_and(data1D_DF["Two Theta"]>=popt_Deg_Window[1]-(sigma_stop)*popt_Deg_Window[2],data1D_DF["Two Theta"]<=popt_Deg_Window[1]-(sigma_stop-1)*popt_Deg_Window[2]))
#
#        Sig_Right_Window=np.where(np.logical_and(data1D_DF["Two Theta"]>=popt_Deg_Window[1]+(sigma_stop-1)*popt_Deg_Window[2],data1D_DF["Two Theta"]<=popt_Deg_Window[1]+(sigma_stop)*popt_Deg_Window[2]))
#
#        #print(Sig_Left_Window, Sig_Right_Window)
#
#        #print("Edge Window: \n", np.concatenate((Sig_Left_Window, Sig_Right_Window), axis=None))
#
#        data1D_DF_BG_Window=data1D_DF.iloc[np.concatenate(([Sig_Left_Window,Sig_Right_Window]), axis=None)]
#
#        baf.save_1D_plot_scatter(save_dir,(peak_name+"BG"),data1D_DF_BG_Window,
#                                title='{} Raw Data, {:d} sig range'.format(peak_name,sigma_stop))
#
#        (popt_BG_Window, pcov_BG_Window)=baf.fit_background(data1D_DF_BG_Window, [popt_Deg_Window[3],popt_Deg_Window[4]] )
#
#
#        baf.save_1D_plot_fit2(save_dir,(peak_name+"Sig_Win_BG"),data1D_DF_Sig_Window, popt_Sig_Window,popt_BG_Window,
#                                title='{} Gaussian fit, {:d} sig range'.format(peak_name,sigma_stop))
#            
#
#    #    baf.save_1D_plot_fit(save_dir,'test5',data1D_DF_Sig_Window,
#    #                         [popt_Sig_Window[0],popt_Sig_Window[1],popt_Sig_Window[2],
#    #                         popt_BG_Window[0],popt_BG_Window[1]],
#    #                            title='Gaussian fit, {:d} sig range'.format(sigma_stop))
#
#
#        summary_row=baf.fit_summary(data1D_DF_Sig_Window, popt_Sig_Window, popt_BG_Window)
#        #print(summary_row)
#        
#        #breakpoint()
#        
#        summary_DF.loc[len(summary_DF)]=[peak_list[i][0]]+summary_row
#
#        #X=hist.data['data'][1][0][start_x:(start_x+window)]
#        #Y=hist.data['data'][1][1][start_x:(start_x+window)]
#        #
#        #
#        #plt.figure(figsize=[10,8])
#        #plt.title('Raw Data, 10 deg range')
#        #plt.scatter(X, Y,color='k',label='Data')
#        ##plt.xlim(78,86)
#        #plt.legend()
#        #plt.show()
#
#
#        #baf.background
#
#    print(summary_DF)
#    
    
    
    return(Submit_dict)



# Irritatingly, there's no clean way to just fit a normal distribution without defining it...

# See https://stackoverflow.com/questions/10582795/finding-the-full-width-half-maximum-of-a-peak
# https://stackoverflow.com/questions/76137714/trying-to-fit-a-gaussian-with-scipy


## Helper functions
def background(x,  m, b):
    '''
    Linear fit of XRD background data.  
    Using a small range, so a more advanced function is not needed
    
    x: x axis of data
    m: slope of line
    b: constant value of line
    '''
    return m*x + b

def gauss(x, A,mu, sigma, m, b):
    '''
    Combined Gaussian and linear fit of XRD background data.  
    Using a small range, so a more advanced function is not needed
    Does not capture the Lorentzian tails well
    
    x: x axis of data
    A: Scale factor
    mu: Center of distribution
    sigma: width of distribution
    m: slope of line
    b: constant value of line
    '''
    return (A/(sigma*np.sqrt(2.0*np.pi)))*np.exp((-(x-mu)**2)/(2.0*sigma**2)) + m*x + b

###



