user_guide

User Guide
=========================


=========================
Background
=========================

In steel materials, several crystal structures or phases can be present.  These are referred to as 'ferrite' - a body centered cubic (BCC) structure, 'austenite' - a face centered cubic (FCC) structure, and 'martensite' - a body centered tetragonal (BCT) structure (but the degree of tetragonality can be small, and this structure is sometimes approximated as BCC).  The amount of each phase, and particularly the proportion of the austenite phase is often important for material properties such as tensile strength, elongation, and fatigue life.

There can be significant disagreement between measurements of phase mixtures in materials. A key to understanding disagreements between measurements is quantification the uncertainty in the measurement and analysis. In our experience, many contributions to the uncertainty are missing in typical phase fraction calculations, leading to misleading interpretations of the accuracy and precision of the measurement. Unfortunately, developing methods to define the sources of uncertainty, quantifying the uncertainty values, and propagating these values through the final calculation are often outside the scope and skill set of those assigned to quantify phase fractions.

There are several existing guides to phase fraction calculations, but each have limits. The ASTM standard [ASTM-E975]_ explicitly restricts usage to 'near random' crystallographic texture, provides tables only for a single composition, and provides tables for only Mo and Cr x-ray radiation. The  Society of Automotive Engineers (SAE) special publication SP-453 [Jatczak-Larson-Shin-1980]_ is more comprehensive in terms of radiation sources and textured materials, but is an information manual and not as prescriptive as a documentary standard.

A round robin performed in 2009 by Jacques *et.* *al.* [Jacques-etal-2009]_ shows current challenges in measureing phase fractions in steels. The paper discusses results from 6 different technqiues.  Even restricting to the x-ray diffraction (XRD) results, large variations between measurements are observed.  When provided in the paper, the uncertainty estimates are much smaller than the range of values.  Examining the summary of experimental procedures, there was also signficant variation in the x-ray wavelength, number of diffraction peaks measured, sample preparation, and analysis methods.

The 'Austenite Calculator' application was developed to offer a more expansive characterization of the uncertainty in phase fraction measurements.  While the application was primarily developed to address the austenite phase fraction in steels, other phase fractions should be possible. This work was inspired by similar efforts of at NIST in developing the web applications 'NIST Consensus Builder' [NIST-ConsensusBuilder-webpage]_ and 'NIST Uncertainty Machine' [NIST-UncertaintyMachine-webpage]_, [Lafarge-Possolo-2015]_.

 

===========================
Details of Implementation
===========================

.. note::
    There are several ways to express phase fractions.  The default in GSAS-II is to describe the phase fraction as a fraction of unit cells.  In metallurgy, phase fraction is often described as a mass fraction (wt %), where the mass of each unit cell is used to determine a phase fraction.  Alternatively, phase fraction can be also expressed as a volume fraction, where the volume of each unit cell is used to determine a phase fraction.

-------------------------------------
Current limitations and assumptions
-------------------------------------

* Absorbtion is similar between the phases
* Spherical grain shapes
* Reflection mode diffraction (not transmission)
* 2D detector gamma is not completely implemented

--------------------------------
Sources of Uncertainty
--------------------------------

Several sources of uncertainty have been considered, but not all are currently implimented.

**Implimented**

* Variation in normalized intensity
* Variation between repeated measurements (samples)
* Uncertainty reported during fitting
* Uncertianty from counting statistics
* Uncertainty from the number of diffracting grains

**Planned**

* Composition uncertainty
* Type of fitting

=========================
Usage
=========================


----------------------
Fitting details
----------------------
Le Bail fitting of individual peaks
Peak selection
Which parameters are fit
Order of parameters fit


=========================
Examples
=========================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Example01
   Example01A
   Example05
   

=========================
References
=========================
.. Using Zotero Quick Copy and Chicago Manual of Style 17th edition (author-date)
    Remove all spaces and replace with hyphens
    Place in alphabetical order

.. [ASTM-E975] ASTM. 2022. “E975-22 Standard Practice for X-Ray Determination of Retained Austenite in Steel with Near Random Crystallographic Orientation.” In ASTM International, 100 Barr Harbor Dr., PO Box C700, West Conshohocken, PA, 19428-2959,(610) 832-9500, E975:1–7.

.. [Jacques-etal-2009] Jacques, P. J., S. Allain, O. Bouaziz, A. De, A.-F. Gourgues, B. M. Hance, Y. Houbaert, et al. 2009. “On Measurement of Retained Austenite in Multiphase TRIP Steels — Results of Blind Round Robin Test Involving Six Different Techniques.” Materials Science and Technology 25 (5): 567–74. https://doi.org/10.1179/174328408X353723.

.. [Jatczak-Larson-Shin-1980] Jatczak, Chester F., John A. Larson, and Steve W. Shin. 1980. Retained Austenite and Its Measurements by X-Ray Diffraction: An Information Manual. Warrendale, PA: Society of Automotive Engineers.

.. [NIST-ConsensusBuilder-webpage] Koepke, Amanda, Thomas LaFarge, Antonio Possolo, and Blaza Toman. n.d. “NIST Consensus Builder.” https://consensus.nist.gov/app/nicob.

.. [NIST-UncertaintyMachine-webpage] Lafarge, Thomas, and Antonio Possolo. 2015. “The NIST Uncertainty Machine.” NCSLI Measure 10 (3): 20–27. https://doi.org/10.1080/19315775.2015.11721732.

.. [Lafarge-Possolo-2015] LaFarge, Thomas, and Antonio Possolo. n.d. “NIST Uncertainty Machine.” NIST Uncertainty Machine. https://uncertainty.nist.gov/.

.. [Toby-2013] Toby, Brian H., and Robert B. Von Dreele. “GSAS-II : The Genesis of a Modern Open-Source All Purpose Crystallography Software Package.” Journal of Applied Crystallography 46, no. 2 (April 1, 2013): 544–49. https://doi.org/10.1107/S0021889813003531.

.. [GSAS-II-github] Toby, Brian H., and Robert B. Von Dreele. "GSAS-II GitHub" https://github.com/AdvancedPhotonSource/GSAS-II

.. [Austenite-Calculator-github] Creuziger, Adam., David Newtwon. "Austenite Calculator" https://github.com/usnistgov/AusteniteCalculator
