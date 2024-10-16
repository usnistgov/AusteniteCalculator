import atmdata
import os
import sys
import math

import pandas as pd
import numpy as np

# orginally plotted using matplotlib, need to convert to plotly for dash
import matplotlib.pyplot as plt

# plotting
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as psub
import pandas as pd
import numpy as np
import plotly.utils as pltu
from plotly.tools import mpl_to_plotly


getElSym = lambda sym: sym.split('+')[0].split('-')[0].capitalize()

def getFormFactors(Elems):
    '''
    This function is from GSAS
    Args:
        Elems: The elements that form factors are needed for

    Returns:
        elemInfo: Form factor information for each element in elems

    Raises:
        
    '''
    elemInfo = []
    if Elems:
        for El in Elems:
            Z = None
            setFormFac = None
            ElemSym = El.strip().upper() #formats elem string...ex(turns  Fe into FE)
            if ElemSym not in elemInfo:
                FormFactors = getFormFactorCoeff(ElemSym)
            for FormFac in FormFactors:
                FormSym = FormFac['Symbol'].strip()
                if FormSym == ElemSym:
                    Z = FormFac['Z']                #At. No.
                    setFormFac = FormFac
            Orbs = GetXsectionCoeff(ElemSym)
            Elem = (ElemSym,Z,setFormFac,Orbs) #The FormFac should always be the non-ionized version of the element ex Fe rather than Fe+3
            elemInfo.append(Elem)
    return elemInfo

def getFormFactorCoeff(El): 
    '''
    This function is from GSAS, a helper function for GetFormFactors
    Args:
        El: The element that a form factor coefficient is needed for

    Returns:
        FormFactors: Returns form factor coefficients for an element

    Raises:
        
    '''
    Els = El.capitalize().strip()
    valences = [ky for ky in atmdata.XrayFF.keys() if Els == getElSym(ky)]
    FormFactors = [atmdata.XrayFF[val] for val in valences]
    for Sy,FF in zip(valences,FormFactors):
        FF.update({'Symbol':Sy.upper()})
    return FormFactors

def GetXsectionCoeff(El):
    """Read atom orbital scattering cross sections for fprime calculations via Cromer-Lieberman algorithm

    :param El: 2 character element symbol
    :return: Orbs: list of orbitals each a dictionary with detailed orbital information used by FPcalc

    each dictionary is:

    * 'OrbName': Orbital name read from file
    * 'IfBe' 0/2 depending on orbital
    * 'BindEn': binding energy
    * 'BB': BindEn/0.02721
    * 'XSectIP': 5 cross section inflection points
    * 'ElEterm': energy correction term
    * 'SEdge': absorption edge for orbital
    * 'Nval': 10/11 depending on IfBe
    * 'LEner': 10/11 values of log(energy)
    * 'LXSect': 10/11 values of log(cross section)

    """
    AU = 2.80022e+7
    C1 = 0.02721
    ElS = El.upper()
    ElS = ElS.ljust(2)
    filename = os.path.join(os.path.split(__file__)[0],'Xsect.dat')
    try:
        xsec = open(filename,'r')
    except:
        print ('**** ERROR - File Xsect.dat not found in directory %s'%os.path.split(filename)[0])
        sys.exit()
    S = '1'
    Orbs = []
    while S:
        S = xsec.readline()
        if S[:2] == ElS:
            S = S[:-1]+xsec.readline()[:-1]+xsec.readline()
            OrbName = S[9:14]
            S = S[14:]
            IfBe = int(S[0])
            S = S[1:]
            val = S.split()
            BindEn = float(val[0])
            BB = BindEn/C1
            Orb = {'OrbName':OrbName,'IfBe':IfBe,'BindEn':BindEn,'BB':BB}
            Energy = []
            XSect = []
            for i in range(11):
                Energy.append(float(val[2*i+1]))
                XSect.append(float(val[2*i+2]))
            XSecIP = []
            for i in range(5): XSecIP.append(XSect[i+5]/AU)
            Orb['XSecIP'] = XSecIP
            if IfBe == 0:
                Orb['SEdge'] = XSect[10]/AU
                Nval = 11
            else:
                Orb['ElEterm'] = XSect[10]
                del Energy[10]
                del XSect[10]
                Nval = 10
                Orb['SEdge'] = 0.0
            Orb['Nval'] = Nval
            D = dict(zip(Energy,XSect))
            Energy.sort()
            X = []
            for key in Energy:
                X.append(D[key])
            XSect = X
            LEner = []
            LXSect = []
            for i in range(Nval):
                LEner.append(math.log(Energy[i]))
                if XSect[i] > 0.0:
                    LXSect.append(math.log(XSect[i]))
                else:
                    LXSect.append(0.0)
            Orb['LEner'] = LEner
            Orb['LXSect'] = LXSect
            Orbs.append(Orb)
    xsec.close()
    return Orbs

def FPcalc(Orbs, KEv):
    """Compute real & imaginary resonant X-ray scattering factors

    :param Orbs: list of orbital dictionaries as defined in GetXsectionCoeff
    :param KEv: x-ray energy in keV
    :return: C: (f',f",mu): real, imaginary parts of resonant scattering & atomic absorption coeff.
    """
    def Aitken(Orb, LKev):
        Nval = Orb['Nval']
        j = Nval-1
        LEner = Orb['LEner']
        for i in range(Nval):
            if LEner[i] <= LKev: j = i
        if j > Nval-3: j= Nval-3
        T = [0,0,0,0,0,0]
        LXSect = Orb['LXSect']
        for i in range(3):
           T[i] = LXSect[i+j]
           T[i+3] = LEner[i+j]-LKev
        T[1] = (T[0]*T[4]-T[1]*T[3])/(LEner[j+1]-LEner[j])
        T[2] = (T[0]*T[5]-T[2]*T[3])/(LEner[j+2]-LEner[j])
        T[2] = (T[1]*T[5]-T[2]*T[4])/(LEner[j+2]-LEner[j+1])
        C = T[2]
        return C
    
    def DGauss(Orb,CX,RX,ISig):
        ALG = (0.11846344252810,0.23931433524968,0.284444444444,
        0.23931433524968,0.11846344252810)
        XLG = (0.04691007703067,0.23076534494716,0.5,
        0.76923465505284,0.95308992296933)
        
        D = 0.0
        B2 = Orb['BB']**2
        R2 = RX**2
        XSecIP = Orb['XSecIP']
        for i in range(5):
            X = XLG[i]
            X2 = X**2
            XS = XSecIP[i]
            if ISig == 0:
                S = BB*(XS*(B2/X2)-CX*R2)/(R2*X2-B2)
            elif ISig == 1:
                S = 0.5*BB*B2*XS/(math.sqrt(X)*(R2*X2-X*B2))
            elif ISig == 2:
                T = X*X2*R2-B2/X
                S = 2.0*BB*(XS*B2/(T*X2**2)-(CX*R2/T))
            else:
                S = BB*B2*(XS-Orb['SEdge']*X2)/(R2*X2**2-X2*B2)
            A = ALG[i]
            D += A*S
        return D 
    
    AU = 2.80022e+7
    C1 = 0.02721
    C = 137.0367
    FP = 0.0
    FPP = 0.0
    Mu = 0.0
    LKev = math.log(KEv)
    RX = KEv/C1
    if Orbs:
        for Orb in Orbs:
            CX = 0.0
            BB = Orb['BB']
            BindEn = Orb['BindEn']
            if Orb['IfBe'] != 0: ElEterm = Orb['ElEterm']
            if BindEn <= KEv:
                CX = math.exp(Aitken(Orb,LKev))
                Mu += CX
                CX /= AU
            Corr = 0.0
            if Orb['IfBe'] == 0 and BindEn >= KEv:
                CX = 0.0
                FPI = DGauss(Orb,CX,RX,3)
                Corr = 0.5*Orb['SEdge']*BB**2*math.log((RX-BB)/(-RX-BB))/RX
            else:
                FPI = DGauss(Orb,CX,RX,Orb['IfBe'])
                if CX != 0.0: Corr = -0.5*CX*RX*math.log((RX+BB)/(RX-BB))
            FPI = (FPI+Corr)*C/(2.0*math.pi**2)
            FPPI = C*CX*RX/(4.0*math.pi)
            FP += FPI
            FPP += FPPI
        FP -= ElEterm
    
    return (FP, FPP, Mu)

def findMu(singular_elem_details, wavelengths, pack_fraction, cell_volume):
    '''
    Args:
        singular_elem_details: numbers about an element needed for the calculation
        wavelengths: x-ray wavelengths
        pack_fractions: Powder packing fraction for the material
        cell_volume: Material cell volume

    Returns:
        ElemSymbol: this is singular_elem_details[0], the elemental symbol for this data
        fps: f' for this element
        fpps: f'' for this element
        mu_converted: mu for this element, converted from barns/atom to cm 

    Raises:
        
    '''
    #print("Find Mu", wavelengths, pack_fraction, cell_volume)
    fps = []
    fpps = []
    Es = []
    Eres = 1.5e-4
    Kev = 12.397639 
    mu_list = []
    for W in wavelengths: #for each wavelength in the instprm files
        E = Kev/W              #maybe get this from instprm file(lam1 converted to energy: google it)
        DE = E*Eres                         #smear by defined source resolution 
        res1 = FPcalc(singular_elem_details[3],E+DE)
        res2 = FPcalc(singular_elem_details[3],E-DE)
        fps.append((res1[0]+res2[0])/2.0)
        fpps.append((res1[1]+res2[1])/2.0)
        Es.append(E)
        mu_list.append(res1[2])
        #print(W, res1, res2)
    
    #print("Mu list:", mu_list)
    mu_avg = sum(mu_list)/len(mu_list) #self.Pack*muT/self.Volume conversion for barns to cm
    mu_converted = (pack_fraction * mu_avg) / cell_volume
    return [singular_elem_details[0], fps, fpps, mu_converted]

def create_graph_data(peak_data, summarized_data):
    '''
    FIX - needs aggregate data for absorption, not just one phase.
    CHECK - SRM example should have similar centriods for first peaks
    
    Args:
       peak_data: Data for the current peak that is being graphed
       summarized_data: A bit of a cheat, but data about the overall phase that the peak needs to know

    Returns:
        df_endpoints: endpoints of graph data created
        df_midpoints: midpoints of graph data created
        Centroid_x: centroid of depth data in x
        Centroid_y: centroid of depth data in y


    Raises:
        
    '''
    Max_intensity_drop=1/1000
    t_max_cm=(1/-summarized_data[2])*np.log(Max_intensity_drop) # change to mu_um?
    t_max_um=t_max_cm*10000 # this would go away
    print(t_max_um) 
    I0=1000000
    steps=25

    x_list=np.linspace(0,t_max_um*np.cos(np.radians(peak_data[2])),num=steps)
    y_list=np.linspace(0,-t_max_um*np.sin(np.radians(peak_data[2])),num=steps)
    df_endpoints = pd.DataFrame(data={'x': x_list, 'y': y_list})
    df_endpoints['length']=np.sqrt(df_endpoints['x']**2+df_endpoints['y']**2)
    df_endpoints['I']=I0 * np.exp(-(summarized_data[2]/10000) * df_endpoints['length'])
    x_mid=[]
    y_mid=[]
    delta_I=[]
    for i in range(0,len(df_endpoints)-1):
        #print(i)
        x_mid.append((df_endpoints['x'].iloc[i]+df_endpoints['x'].iloc[i+1])/2)
        y_mid.append((df_endpoints['y'].iloc[i]+df_endpoints['y'].iloc[i+1])/2)
        delta_I.append(df_endpoints['I'].iloc[i]-df_endpoints['I'].iloc[i+1])
    
    df_mid = pd.DataFrame(data={'x_mid': x_mid, 'y_mid': y_mid, 'delta_I':delta_I})
    # It's not clear to me how this should properly be calculated.  
    # f_prime can occasionally take positive values at higher energies.
    # That seems to imply a flourescing photon can cause additional scattering?

    # For now I am using rule of mixtures with absolute values
    df_mid['travel_dist']=np.sqrt(df_mid['x_mid']**2+df_mid['y_mid']**2)

    df_mid['absorbed']=df_mid['delta_I']*(summarized_data[1]/(summarized_data[1]+abs(summarized_data[0])+peak_data[0]))
    df_mid['anomalous']=df_mid['delta_I']*(abs(summarized_data[0])/(summarized_data[1]+abs(summarized_data[0])+peak_data[0]))
    df_mid['scattered']=df_mid['delta_I']*(peak_data[0]/(summarized_data[1]+abs(summarized_data[0])+peak_data[0]))

    #scattered, but not absorbed on return to the surface
    df_mid['Escaped']=df_mid['scattered'] *  np.exp(-(summarized_data[2]/10000) * df_mid['travel_dist'])
    df_mid['RelativeEscaped']=df_mid['Escaped']/I0
    
    Centroid_y=np.sum(df_mid['Escaped']*df_mid['y_mid'])/np.sum(df_mid['Escaped'])
    Centroid_x=np.sum(df_mid['Escaped']*df_mid['x_mid'])/np.sum(df_mid['Escaped'])

    return [df_endpoints, df_mid, Centroid_x, Centroid_y, peak_data[2]]

#def transmission_mode_data(peak_data, summarized_data):


def create_centroid_plot(df_mid, Centroid_y):
    '''
    Plots x-ray depth over material and centroid of data
    Args:
        df_mid: midpoints of graph data for current peak
        Centroid_y: centroid in y

    Returns:
       fig: Plotly graph of centroid data

    Raises:
        
    '''
    #plt.barh( df_mid['y_mid'],df_mid['Escaped'],color='0.9')
    #plt.plot( df_mid['Escaped'], df_mid['y_mid'], 'ko', linestyle="-")
    #plt.hlines(Centroid_y, 0, df_mid['Escaped'].iloc[0], color='0.3',linestyle="--")

    #print(df_mid,Centroid_y)
    
    #Swap X and Y for horizontal bar chart
    trace1 = go.Bar(
        x=df_mid['RelativeEscaped'],
        y=df_mid['y_mid'],
        orientation='h',
        marker=dict(
            color='rgb(200,200,200)'
                )
    )

# Don't know why the markers aren't working
    trace2 = go.Scatter(
        x=df_mid['RelativeEscaped'],
        y=df_mid['y_mid'],
        marker=dict(
            color='rgb(0,0,0)', size=50,symbol='circle'
                )
    )
    

    fig = psub.make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_hline(y=Centroid_y, line_dash="dot")

# Need a better way of passing the shape parameters
# Add a shape
#    fig.add_shape(type="circle",
#        xref="paper", yref="y",
#        layer="below",
#        opacity=0.5,
#        fillcolor="PaleTurquoise",
#        x0=0, y0=0, x1=.9, y1=-40,
#        line_color="PaleTurquoise",
#)

    fig['layout'].update(height = 600, width = 800, title = "",xaxis=dict(
                     tickangle=0),
                     xaxis_title="Scattered x-rays (normalized by flux)",
                     yaxis_title="Z-depth in Fe (microns)",
                     font=dict(size=18),
                     showlegend=False
                    )
    return fig

def create_depth_plot(x_list, y_list, theta_deg):
    '''
    Plots x-ray depth visually
    Args:
        x_list: list of data in x
        y_list: list of data in y
        theta_deg: theta of current peak

    Returns:
       fig: Plotly graph of depth data

    Raises:
        
    '''
    #start x-ray height
    xray_start=50 


    trace1 = go.Scatter(
        x=x_list,
        y=y_list,
        orientation='h',
        marker=dict(
            color='rgb(0,0,0)'
                )
    )

    # Don't know why the markers aren't working
    trace2 = go.Scatter(
        x=[-xray_start/np.tan(np.radians(theta_deg)),0],
        y=[xray_start,0],
        marker=dict(
            color='rgb(0,0,255)'
                )
    )

    #plt.xlim(-50,50)
    #plt.ylim(-50,50)
    #plt.gca().set_aspect('equal')

    fig = psub.make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_hline(y=0)
    fig['layout'].update(height = 800, width = 800, title = "",xaxis=dict(
                     tickangle=0),
                     xaxis_title="X position (microns)",
                     yaxis_title="Z-depth in Fe (microns)",
                     font=dict(size=18),
                     showlegend=False
                    )

    fig.update_xaxes(range=[-50, 50])
    fig.update_yaxes(range=[-50, 50])

    return fig

def crystallites_illuminated_calc(crystal_data, phase_frac, powder_size, crystalites_per_particle, multiplicity, theta_deg, d_t_half):

    #CHECK-WHAT PHASE FRACTION SHOULD BE USED?  I THINK VOLUME, NOT NUMBER OF CELLS

    '''
    Calculate crystallites illuminated data for a peak
    Args:
        crystal_data: dict of data about crystal
        phase_frac: phase fraction of phase that the peak belongs to
        powder_size: Powder size of the phase that the peak belongs to
        crystalites_per_particle: Crystallites per particle for the phase that the peak belongs to
        multiplicity: peak multiplicity
        theta_deg: Theta of current peak

    Returns:
       N_layers: number of layers of particles illuminated
       N_illuminated: Number of particles illuminated
       diffracting_fraction: Diffracting Fraction
       N_diffracted: number of particles diffracted, represented by N_illuminated*diffracting_fraction
    Raises:
        
    '''
    
    #Follows nomenclature of ASTM E112
    
    #print("passed")
    #print(crystal_data, phase_frac, powder_size, crystalites_per_particle, multiplicity, theta_deg, d_t_half)
    
    D_bar = powder_size/1000 # convert from micrometers to millimeters
    l_bar= D_bar/1.5 #Inverse of ASTM E112 A2.9; mean lineal intercept length
    A_bar = ((l_bar)**2)*(4/np.pi) # Inverse of ASTM E112 A2.8; average grain cross sectional area
    N_bar_A = 1/A_bar # Inverse of ASTM E112 A2.7; number of grains per unit area

    # if the penetration depth is less than particle size, set layers=1
    if l_bar<D_bar:
        N_layers=1
    # else find the number of layers illuminated
    else:
        N_layers=D_bar/l_bar

    #print(D_bar,l_bar,A_bar, N_bar_A)
    raster_area_mm=(crystal_data['raster_x']+crystal_data['beam_size'])*(crystal_data['raster_y']+crystal_data['beam_size'])
    #print(raster_area_mm)
    phase_fraction = phase_frac

    N_illuminated=N_bar_A*raster_area_mm*phase_fraction*crystalites_per_particle*N_layers

    #For cases where more grains through the thickness are illuminated
    #sample_thickness_mm=30
    #N_l_bar=1/l_bar
    #print(N_l_bar)

    #print(N_bar_A,N_l_bar,raster_area_mm,sample_thickness_mm,phase_fraction,crystalites_per_particle)

    #N_illuminated=N_bar_A*N_l_bar*raster_area_mm*sample_thickness_mm*phase_fraction*crystalites_per_particle
    #print(N_illuminated)

    delta_theta_half=(d_t_half)*(np.pi/180)
    # print(d_t_half, delta_theta_half)
    # gamma replaces H_R/L for 2D detector
    gamma = (15)*(np.pi/180)
    

    diffracting_fraction=((multiplicity/4*np.pi)*
                          (crystal_data['W_F']/crystal_data['L']+
                           delta_theta_half)*
                      (crystal_data['H_F']/crystal_data['L']+
                      crystal_data['H_R']/crystal_data['L'])*
                      (1/(2*(np.sin(theta_deg*np.pi/180)))))

#    print("Crystallites Illuminated Values")
#    print("Crystal Data")
#    print(crystal_data)
#    print("Two theta, Multiplicity, Phase Fraction, N_illuminated, diffracting_fraction, N_illuminated * diffracting_fraction")
#    print(2*theta_deg, multiplicity,phase_fraction, N_illuminated, diffracting_fraction, N_illuminated * diffracting_fraction)
#    print("\n")

    return N_layers, N_illuminated, diffracting_fraction, N_illuminated * diffracting_fraction
