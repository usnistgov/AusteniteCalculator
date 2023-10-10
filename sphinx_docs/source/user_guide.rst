user_guide

Welcome to the user guide
=========================


=========================
Overview
=========================

There can be significant disagreement between measurements of phase mixtures in materials.  This application was developed primarily to adddress the austenite phase fraction in steels.
A key to understanding disagreements between measurements is quantifyication the uncertainty in the measurement and analysis. In our experience, many contributions to the uncertainty are missing in typical calculations, leading to misleading interpretations of the accuracy and precision of the measurement. Unfortunately, developing methods to define the sources of uncertainty, quantifying the uncertainty values, and propagating these values through the final calculation are often outside the scope and skill set of those assigned to quantify phase fractions.

Existing practice guides have some limits. [ASTM-E975-2013]_ explicity restricts usage to 'near random' crystallographic texture, provides tables only for a single composition and Mo and Cr x-ray radiation.  [Jatczak-Larson-Shin-1980]_ .

[Jacques-etal-2009]_ round robin

Inspired by similar efforts of the [NIST-ConsensusBuilder-webpage]_, [NIST-UncertaintyMachine-webpage]_, [Lafarge-Possolo-2015]_

===========================
Details of Implimentation
===========================

.. note::
    There are several ways to express phase fractions.  The default in GSAS-II is to describe the phase fraction as a fraction of unit cells.  In metallurgy, phase fraction is often described as a mass fraction (wt %), where the mass of each unit cell is used to determine a phase fraction.  Alternatively, phase fraction can be also expressed as a volume fraction, where the volume of each unit cell is used to determine a phase fraction.

---------------------
Software
---------------------

GSAS-II
Python script using scripting toolkit (name?)
Dash, Docker

----------------------
Fitting details
----------------------
Le Bail fitting of individual peaks
Peak selection
Which parameters are fit
Order of parameters fit

--------------------------------
Instrument Parameter Creation
--------------------------------


--------------------------------
Sources of Uncertainty
--------------------------------

.. I don't know why this isn't formatting right

Several sources of uncertainty have been considered

**Implimented**
* Variation in normalized intensity
* Variation between samples
* Fit uncertainty
* Counting statistics

**Planned**
* Number of diffracting grains (interaction volume)
* Composition uncertainty

=========================
Usage
=========================
(add demo or instructions here?  Or elsewhere?)

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   CrystallitesIlluminatedFileCreation
   InstrumentFileCreation

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

.. [ASTM-E975-2013] ASTM. 2013. “E975-13 Standard Practice for X-Ray Determination of Retained Austenite in Steel with Near Random Crystallographic Orientation.” In ASTM International, 100 Barr Harbor Dr., PO Box C700, West Conshohocken, PA, 19428-2959,(610) 832-9500, E975:1–7.

.. [Jacques-etal-2009] Jacques, P. J., S. Allain, O. Bouaziz, A. De, A.-F. Gourgues, B. M. Hance, Y. Houbaert, et al. 2009. “On Measurement of Retained Austenite in Multiphase TRIP Steels — Results of Blind Round Robin Test Involving Six Different Techniques.” Materials Science and Technology 25 (5): 567–74. https://doi.org/10.1179/174328408X353723.

.. [Jatczak-Larson-Shin-1980] Jatczak, Chester F., John A. Larson, and Steve W. Shin. 1980. Retained Austenite and Its Measurements by X-Ray Diffraction: An Information Manual. Warrendale, PA: Society of Automotive Engineers.

.. [NIST-ConsensusBuilder-webpage] Koepke, Amanda, Thomas LaFarge, Antonio Possolo, and Blaza Toman. n.d. “NIST Consensus Builder.” https://consensus.nist.gov/app/nicob.

.. [NIST-UncertaintyMachine-webpage] Lafarge, Thomas, and Antonio Possolo. 2015. “The NIST Uncertainty Machine.” NCSLI Measure 10 (3): 20–27. https://doi.org/10.1080/19315775.2015.11721732.

.. [Lafarge-Possolo-2015] LaFarge, Thomas, and Antonio Possolo. n.d. “NIST Uncertainty Machine.” NIST Uncertainty Machine. https://uncertainty.nist.gov/.




