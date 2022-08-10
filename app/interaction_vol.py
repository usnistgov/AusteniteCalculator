def getElems():
    elems = []
    return elems

def getFormFactors():
    if Elems:
        for El in Elems:
            ElemSym = El.strip().upper() #formats elem string...ex(turns  Fe into FE)
            if ElemSym not in ElList:
            FormFactors = G2elem.GetFormFactorCoeff(ElemSym)
            for FormFac in FormFactors:
            FormSym = FormFac['Symbol'].strip()
            if FormSym == ElemSym:
            Z = FormFac['Z']                #At. No.
            Orbs = G2elem.GetXsectionCoeff(ElemSym)
            Elem = (ElemSym,Z,FormFac,Orbs)
        self.Elems.append(Elem)
    return None

def findElemfs():
    for Elem in self.Elems:
        Els = Elem[0]
        Els = Els = Els.ljust(2).lower().capitalize()
        Wmin = self.Wmin
        Wmax = self.Wmax
        Z = Elem[1]
        if Z > 78: Wmin = 0.16        #heavy element high energy failure of Cromer-Liberman
        if Z > 94: Wmax = 2.67        #heavy element low energy failure of Cromer-Liberman
        lWmin = math.log(Wmin)
        N = int(round(math.log(Wmax/Wmin)/self.Wres))    #number of constant delta-lam/lam steps
        I = range(N+1)
        Ws = []
        for i in I: Ws.append(math.exp(i*self.Wres+lWmin))
        fps = []
        fpps = []
        Es = []
        for W in Ws:
            E = self.Kev/W
            DE = E*self.Eres                         #smear by defined source resolution
            res1 = G2elem.FPcalc(Elem[3],E+DE)
            res2 = G2elem.FPcalc(Elem[3],E-DE)
            fps.append((res1[0]+res2[0])/2.0)
            fpps.append((res1[1]+res2[1])/2.0)
            Es.append(E)
        if self.ifWave:
            Fpps = (Els,Ws,fps,fpps)
        else:
            Fpps = (Els,Es,fps,fpps)
        FPPS.append(Fpps)
    return None

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