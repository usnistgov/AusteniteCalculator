import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
import json
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


def fit_peaks_LeBail_assist(hist, LeBail_peaks_list, Chebyschev_coeffiecients=5):
    """Subroutine to fit data using peaks found from LeBail fitting

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

    # Add peak location and area
    for i in range(len(LeBail_peaks_list['pos'])):
        #print(LeBail_peaks_list['LeBail_Int'][i], LeBail_peaks_list['pos'][i])
        hist.add_peak(LeBail_peaks_list['LeBail_Int'][i],ttheta=LeBail_peaks_list['pos'][i] )
        
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

    # Fifth, pos and area
    hist.set_peakFlags(pos=True, area=True)
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


def fit_peaks_Rowles(datadir,workdir,G2sc,cif_fnames,xrdml_fname,instprm_fname,json_data,flags_for_user_DF,Chebyschev_coeffiecients=5):

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
    
    data_path_wrap = lambda fil: datadir + '/' + fil
    save_wrap = lambda fil: workdir + '/' + fil
    
    print("Fitting entire pattern\n")
    
    gpx = G2sc.G2Project(newgpx=save_wrap('LeBail_fit.gpx'))
    

    
    # Read in phases
    for phase_file in cif_fnames:
        gpx.add_phase(data_path_wrap(phase_file),fmthint='CIF') # add a phase to the project
    
    # Read in histogram
    hist = gpx.add_powder_histogram(data_path_wrap(xrdml_fname),
                                    data_path_wrap(instprm_fname),
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
                 columns=['h','k','l','mul','d','pos','sig','gam',
                 'F_obs_sq','F_calc_sq','phase','I_corr','Prfo','Trans','ExtP'])
                LeBail_reflist_DF[['Phase']] = phase.name
                #print(LeBail_reflist_DF)
            # otherwise append
            else:
                LeBail_reflist2_DF=pd.DataFrame(i.data["Reflection Lists"][phase.name]["RefList"],
                 columns=['h','k','l','mul','d','pos','sig','gam',
                 'F_obs_sq','F_calc_sq','phase','I_corr','Prfo','Trans','ExtP'])
                LeBail_reflist2_DF[['Phase']] = phase.name
                LeBail_reflist_DF=pd.concat([LeBail_reflist_DF,LeBail_reflist2_DF],axis=0,ignore_index=True)
                #print(LeBail_reflist_DF)
                #print(LeBail_reflist2_DF)
            
            
            
    LeBail_reflist_DF = LeBail_reflist_DF.sort_values(by='pos')
    LeBail_reflist_DF = LeBail_reflist_DF.reset_index(drop=True)
    # Calculate an intensity
    LeBail_reflist_DF['LeBail_Int']=LeBail_reflist_DF['I_corr']*LeBail_reflist_DF['F_calc_sq']

    print("Reflection List DataFrame")
    print(LeBail_reflist_DF)
            
    #### Flags

    # Note the sample displacement
    print("Sample Displacement Found")
    flags_for_user_DF=compute_results.flag_phase_fraction(np.nan,
    "Sample Displacement","A sample displacement (shift) value of: "+"{:.4f}".format(hist.data["Sample Parameters"]['Shift'][0])+" um was fit",
    "Check goniometer alignment if this value is large",
     DF_to_append=flags_for_user_DF)

    # Note the microstrain?
    
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
    return(LeBail_reflist_DF.to_dict(), flags_for_user_DF)
