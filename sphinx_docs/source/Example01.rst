Example 01 - Withdrawn NIST 487 SRM
==========================================

=========================
Background
=========================

The National Institute of Standards and Technology (NIST, formerly the National Bureau of Standards or NBS) develops Standard Reference Materials (SRMs) and Reference Materials (RMs) for the support of accurate and compatible measurements.

The SRM 487 series were developed to nominally have volume percents of 30% retained austenite mixed with 70% martensite, obtained by combining AISI 310 and AISI 430 stainless steel powders.  These phase fractions were measured with x-ray fluorescence (XRF) and optical microscopy after etching; but were not measured with x-ray diffraction.  Subsequent disagreement between the x-ray diffraction measurement and the certified values lead to the SRM 487 series being withdrawn as an SRM. More information is available at [NBS SRM-487]_

While SRM 487 is no longer approved as an SRM, it remains a well documented and characterized sample, and was used an an example material.  As noted, the set of SRM 487 samples were created to have approximately 30% austenite.  The particular sample identifier "157" has a value inscribed of 32.46%, derived from the XRF value and uncertainty of 0.5% [NBS SRM-487]_.  Note that the precise value is likely unreliable and the reason this SRM series was withdrawn.

=========================
File Creation
=========================


SRM 487 and a LaB6 660c SRM for instrument calibration were scanned on a Bruker D8 Discover. A 1 mm circular aperture and 4 mm raster in x and y was used.  The W_F and H_F were set to 1 to match the circular aperture.  As a 2D detector was used, the 1D pattern was summed from a 16 degree (+/- 8 deg) angular window, which corresponds to slightly more than 70 mm H_R. The system was well aligned, so an initial sample_displacement value was set to 0.  **Check details of optics and scan settings.** Instrument file creation used the same settings and used the tutorial [GSAS-II-FindProfParamCW]_.

[NBS SRM-487]_ provides the chemical compositions in weight percent, these were translated to atomic fractions.  Of the elements listed, only Fe, Cr, Si, Mn, C, Ni were used and the atomic fraction of these elements were summed to 1.  Preliminary fitting in GSAS-II was used to approximate the unit cell size and create the .cif files. **Source for Uiso?**  The martensite was approximated as body centered cubic (BCC) as there was a low fraction of carbon.  No significant tetragonality was noted in the fits or patterns.

[NBS SRM-487]_ also provided the mesh ranges for powder particle sizes for the austenite and martensite.  These were converted to approximate sizes in micrometers of 50 micrometers and 40 micrometers respectively. The number of crystallites per powder particle was not measured, so 10 crystallites per particle was used as that would be an upper limit on uncertainty (fewer crystallites illuminated).  As the powdering process likely induces rapid solidification, a rocking angle of 1 degree was used.


=========================
Results
=========================
.. list output with version number


'Intensity Plots'
Peak fit generally gives a closer fit to the data
F110 leading edge (lower two theta) not as well captured.  Both fit types struggle on F211, but area is pretty consistent.  17.7740 sample displacement


'Normalized Intensities'
Offset between normalized intensities between Le Bail and individual peak fit methods.  Ferrite 200 noticeably below the other data points.  Downward slope in both phases as a function of two theta. No 

