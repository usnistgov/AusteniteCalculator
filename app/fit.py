import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

def fit_peaks(hist, peaks_list, Chebyschev_coeffiecients=5):
    """Subroutine to fit data using LeBail fitting

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
        #print("peak location ", peak)
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


def fit_moved_left_peaks(hist, peaks_list, peak_verify):
    """Subroutine to fit data using LeBail fitting, shifting peaks to the left (lower 2-theta)

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
    temp_list = {}
    for x in range(len(peak_verify)):
        if(not(peak_verify[x])):
            temp_list.append(peaks_list[x])

    # First fit only the area
    hist.set_peakFlags(peaklist=temp_list, area=True)
    hist.refine_peaks(mode = 'hold')
            
    # Second, fit the area and position
    hist.set_peakFlags(peaklist=temp_list, pos=True,area=True)
    hist.refine_peaks(mode = 'hold')

    # Third, fit the area, position, and gaussian componenet of the width
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True,sig=True, gam = True)
    hist.refine_peaks(mode = 'hold')

def fit_moved_right_peaks(hist, peaks_list, peak_verify):
    """Subroutine to fit data using LeBail fitting, shifting peaks to the right (higher 2-theta)

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
    temp_list = []
    for x in range(len(peak_verify)):
        if(not(peak_verify[x])):
            temp_list.append(peaks_list[x])

    # First fit only the area
    hist.set_peakFlags(peaklist = temp_list, area=True)
    hist.refine_peaks(mode = 'hold')
            
    # Second, fit the area and position
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True)
    hist.refine_peaks(mode = 'hold')

    # Third, fit the area, position, and gaussian componenet of the width
    hist.set_peakFlags(peaklist = temp_list, pos=True,area=True,sig=True, gam = True)
    hist.refine_peaks(mode = 'hold')   

def fit_peaks_holdsig(hist, peaks_list, Chebyschev_coeffiecients, peak_verify):
    """Subroutine to fit data using LeBail fitting, but hold the sigma value

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
        #print("peak location ", peak)
    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    temp_list = []
    for x in range(len(peak_verify)):
        if(not(peak_verify[x])):
            temp_list.append(peaks_list[x])
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
    """Subroutine to fit data using LeBail fitting, holding gamma value

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
        #print("peak location ", peak)
    # Use this order (based on Vulcan process)
    #? otherwise fitting gets unstable
    #? How to make the fitting more stable?
    #? Often get fits in the wrong location.  Use fit data to estimate a0 and recycle?
    #? What to do when signal to noise is poor?  Ways to use good fits to bound parameters for poor fits?
    temp_list = []
    for x in range(len(peak_verify)):
        if(not(peak_verify[x])):
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
            # print(index, hist.data['data'][1][0][index],hist.data['data'][1][4][index])
        print("Counts: ",back_counts,fit_counts,data_counts,data_counts-back_counts, peak[2]/(data_counts-back_counts) )
        #print(peak[2],back_counts,peak[2]/back_counts,"\n")
        #print(peak[2]/math.sqrt(back_counts+peak[2]))
        #print(peak[2],back_counts,back_counts+peak[2], math.sqrt(back_counts+peak[2]))
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

    max = 0
    for x in range(t_int.shape[0]):
        if(t_int[x] > t_int[max]):
            max = x

    # Check if intensities are positive
    for x in range(t_int.shape[0]):
        if(t_int[x] < 0):
            verify_list[x] = False
        else:
            verify_list[x] = True
            print("All Intensities Positive")

    # Check if sig, gam values are reasonable
    # Leading to a number of rejected peaks currently
    m, b = np.polyfit(t_pos, t_sigma, 1)

    for x in range(t_pos.shape[0]):
        print("\n \n Line of best fit value")
        print(t_sigma[x], " = ", m, " * ", t_pos[x], " + ", b)
        print("\n\n")
        if(t_sigma[x] > (m * t_pos[x] + b) + t_sigma[max]/2 or t_sigma[x] < (m * t_pos[x] + b) - t_sigma[max]/2):            
            verify_list[x] = False

    m, b = np.polyfit(t_pos, t_gamma, 1)

    for x in range(t_pos.shape[0]):
        if(t_gamma[x] > (m * t_pos[x] + b) + t_gamma[max]/2 or t_gamma[x] < (m * t_pos[x] + b) - t_gamma[max]/2):
            verify_list[x] = False


    print("Peak Verificaiton List \n", verify_list)

    return verify_list
    #return flags_DF
