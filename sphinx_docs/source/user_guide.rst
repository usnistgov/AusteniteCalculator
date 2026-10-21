user_guide

******************************
User Guide
******************************


==============================
Background
==============================

In steel materials, several crystal structures or phases can be present.  These are referred to as 'ferrite' - a body centered cubic (BCC) structure, 'austenite' - a face centered cubic (FCC) structure, and 'martensite' - a body centered tetragonal (BCT) structure (but the degree of tetragonality can be small, and this structure is sometimes approximated as BCC).  The amount of each phase, and particularly the proportion of the austenite phase is often important for material properties such as tensile strength, elongation, and fatigue life.

There can be significant disagreement between measurements of phase mixtures in materials. A key to understanding disagreements between measurements is quantification the uncertainty in the measurement and analysis. The authors have observed that many contributions to the uncertainty are missing in typical phase fraction calculations, leading to misleading interpretations of the accuracy and precision of the measurement. Unfortunately, developing methods to define the sources of uncertainty, quantifying the uncertainty values, and propagating these values through the final calculation are often outside the scope and skill set of those assigned to quantify phase fractions.

There are several existing guides to phase fraction calculations, but each have limits. The ASTM standard [ASTM-E975]_ explicitly restricts usage to 'near random' crystallographic texture, provides tables only for a single composition, and provides tables for only Mo and Cr x-ray radiation. The  Society of Automotive Engineers (SAE) special publication SP-453 [Jatczak-Larson-Shin-1980]_ is more comprehensive in terms of radiation sources and textured materials, but is an information manual and not as prescriptive as a documentary standard.

A round robin performed in 2009 by Jacques *et.* *al.* [Jacques-etal-2009]_ shows current challenges in measuring phase fractions in steels. The paper discusses results from 6 different techniques.  Even restricting to the x-ray diffraction (XRD) results, large variations between measurements are observed.  When provided in the paper, the uncertainty estimates are much smaller than the range of values.  Examining the summary of experimental procedures, there was also significant variation in the x-ray wavelength, number of diffraction peaks measured, sample preparation, and analysis methods.

The 'Austenite Calculator' application was developed to offer a more expansive characterization of the uncertainty in phase fraction measurements.  While the application was primarily developed to address the austenite phase fraction in steels, other phase fractions should be possible. This work was inspired by similar efforts of at NIST in developing the web applications such as the 'NIST Consensus Builder' [NIST-ConsensusBuilder-webpage]_ and 'NIST Uncertainty Machine' [NIST-UncertaintyMachine-webpage]_, [Lafarge-Possolo-2015]_.

The code for the Austenite Calculator is available on GitHub: [Austenite-Calculator-github]_.  This software builds on the GSAS-II diffraction analysis package [Toby-2013]_ [GSAS-II-github]_, using the *GSASIIscriptable* module. JavaScript is used to render the plots, and Podman (or Docker) is used as a container for the application.
 
.. note::
    There are several ways to express phase fractions.  The default in GSAS-II is to describe the phase fraction as a fraction of unit cells.  In metallurgy, phase fraction is often described as a mass fraction (or more commonly weight percent [wt %]), where the mass of each unit cell is used to determine a phase fraction.  Alternatively, phase fraction can be also expressed as a volume fraction, where the volume of each unit cell is used to determine a phase fraction.  The Austenite Calculator application allows the user to select between these conventions and encourages users to be explicit about their choice when reporting values.


==============================
Details of Implementation
==============================
-------------------------------------
Assumptions and Current Limitations
-------------------------------------

* Absorption is similar between the phases **(microabsorption is not addressed)**
* Spherical grain shapes **(grain aspect ratio is not addressed)**
* 'l_bar_um' is the 'mean lineal intercept length' as described in [ASTM-E112]_
* The nomenclature and definitions from [Alexander-1948]_ were used in this work to determine the number of crystallites diffracting.
* Reflection mode diffraction **(transmission is not currently supported)**
* 2D detector gamma is not completely implemented

--------------------------------
Sources of Uncertainty
--------------------------------

Several sources of uncertainty have been considered, but not all are currently implemented.  The values in parenthesis are the function names for the uncertainty source.

**Implemented**

* Variation between repeated measurements (sigma_sample)
* Variation in normalized intensity (sigma_exp)
* Uncertainty from counting statistics (u_count_fit)
* Uncertainty reported during fitting (u_int_fit)
* Uncertainty from the number of diffracting grains (u_N_Diffracting_95pct)

**Planned**

* Composition uncertainty
* Type of fitting

As of the 0.1.0 release, individual peak fit (_fit) and Le Bail (_LB) fits are performed.  The individual peak fit values are used in the phase fraction calculation, but the Le Bail fit is used to provide initial values and a consistency check.  There are additional references to a ‘G’ is for Gaussian only fit, and ‘TR’ for trapezoidal rule integration of the peak which are partially implemented, but are not used in the phase fraction.


==============================
Examples
==============================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Example01

==============================
References
==============================
.. Using Zotero Quick Copy and Chicago Manual of Style 17th edition (author-date)
    Remove all spaces and replace with hyphens
    Place in alphabetical order

.. [Alexander-1948] Alexander, Leroy, Harold P. Klug, and Elizabeth Kummer. 1948. “Statistical Factors Affecting the Intensity of X‐Rays Diffracted by Crystalline Powders.” Journal of Applied Physics 19 (8): 742–53. https://doi.org/10.1063/1.1698200.

.. [ASTM-E975] ASTM. 2022. “E975-22 Standard Practice for X-Ray Determination of Retained Austenite in Steel with Near Random Crystallographic Orientation.” In ASTM International, 100 Barr Harbor Dr., PO Box C700, West Conshohocken, PA, 19428-2959,(610) 832-9500, E975:1–7.

.. [ASTM-E112] ASTM. 2004. “E112-04 ASTM E112-04: Standard Test Methods for Determining Average Grain Size.” In ASTM International, 100 Barr Harbor Dr., PO Box C700, West Conshohocken, PA, 19428-2959,(610) 832-9500, E112:1–26.

.. [Austenite-Calculator-github] Creuziger, Adam., David Newtwon. "Austenite Calculator" https://github.com/usnistgov/AusteniteCalculator

.. [GSAS-2004] Larson, Allen C, and Robert B Von Dreele. 2004. “GSAS - General Structure Analysis System.” LAUR 86-748. Los Alamos National Laboratory.

.. [GSAS-II-github] Toby, Brian H., and Robert B. Von Dreele. "GSAS-II GitHub" https://github.com/AdvancedPhotonSource/GSAS-II

.. [GSAS-II-DevDoc] Von Dreele, Robert B. and Brian H. Toby. "GSAS-II Developer’s Documentation" https://gsas-ii.readthedocs.io/en/latest/

.. [GSAS-II-FindProfParamCW] "Create Instrument Parameter File: Determine Starting Profile from a Standard" https://subversion.xray.aps.anl.gov/pyGSAS/Tutorials/CWInstDemo/FindProfParamCW.htm

.. [Jacques-etal-2009] Jacques, P. J., S. Allain, O. Bouaziz, A. De, A.-F. Gourgues, B. M. Hance, Y. Houbaert, et al. 2009. “On Measurement of Retained Austenite in Multiphase TRIP Steels — Results of Blind Round Robin Test Involving Six Different Techniques.” Materials Science and Technology 25 (5): 567–74. https://doi.org/10.1179/174328408X353723.

.. [Jatczak-Larson-Shin-1980] Jatczak, Chester F., John A. Larson, and Steve W. Shin. 1980. Retained Austenite and Its Measurements by X-Ray Diffraction: An Information Manual. Warrendale, PA: Society of Automotive Engineers.

.. [Lafarge-Possolo-2015] LaFarge, Thomas, and Antonio Possolo. n.d. “NIST Uncertainty Machine.” NIST Uncertainty Machine. https://uncertainty.nist.gov/.

.. [NBS SRM-487] Hicho, G. E. and E. E. Eaton. 1982. "A Standard Reference Material Containing Nominally Thirty Percent Austenite (SRM 487)" NBS Special Publication 260-78 https://doi.org/10.6028/NBS.SP.260-78

.. [NIST-ConsensusBuilder-webpage] Koepke, Amanda, Thomas LaFarge, Antonio Possolo, and Blaza Toman. n.d. “NIST Consensus Builder.” https://consensus.nist.gov/app/nicob.

.. [NIST-UncertaintyMachine-webpage] Lafarge, Thomas, and Antonio Possolo. 2015. “The NIST Uncertainty Machine.” NCSLI Measure 10 (3): 20–27. https://doi.org/10.1080/19315775.2015.11721732.

.. [Rowles-2021] Rowles, Matthew R. 2021. "The effect of data quality and model parameters on the quantitative phase analysis of X-ray diffraction data by the Rietveld method" Journal of Applied Crystallography. 54 (3): 878-894. https://doi.org/10.1107/S160057672100371X

.. [Toby-2013] Toby, Brian H., and Robert B. Von Dreele. “GSAS-II : The Genesis of a Modern Open-Source All Purpose Crystallography Software Package.” Journal of Applied Crystallography 46, no. 2 (April 1, 2013): 544–49. https://doi.org/10.1107/S0021889813003531.




