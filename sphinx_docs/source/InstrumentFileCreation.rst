InstrumentFileCreation
=========================


=========================
Background
=========================
In addition to the X-Ray Diffraction File(s) and the Crystallographic Information Files (.cif), two additional files are needed to analyze the XRD data: an Instrument Parameter File (.instprm) and a Crystallites Illuminated JSON File (.json).


=========================
File Description
=========================

The Instrument Parameter File uses the conventions [GSAS-2004]_. Depending on the type of setup, there may be differences in the file.  The [GSAS-2004]_ guide gives some examples of the profile functions on pages 143 to 165.

Parameters (constant wavelength, type 3):

- Type: Type of diffraction data (GSAS histogram type). The histogram type flags indicate the type of sample (P: powder or S: single crystal), type of radiation (N: neutron or X: x-rays), type of data (T: time of flight, C: constant wavelength or E: x-ray energy dispersive)
- Bank: Detector bank ID
- Lam (Lam1,Lam2): wavelengths (lambda) for xrays/neutrons
- Zero: Zero Point Correction factor
- Polariz.: Polarization of the xrays/neutrons
- Azimuth: Detector azimuthal angle (?)
- I(L2)/I(L1): Ratio of incoming wavelenths
- U: Gaussian width parameter
- V: Gaussian width parameter
- W: Gaussian width parameter
- X: Lorentzian width parameter
- Y: Lorentzian width parameter
- Z: Lorentzian width parameter
- SH/L: "H" and "S" correspond to the sample and detector hights, and "L" is the diffractometer radius
- Source:

Parameters (constant wavelength):
'Type',
'fltPath',
'2-theta',
'difC',
'difA',
'difB',
'Zero',
'alpha',
'beta-0',
'beta-1',
'beta-q',
'sig-0',
'sig-1',
'sig-2',
'sig-q',
'X',
'Y',
'Z',
'Azimuth',



=========================
Usage
=========================
The approach following the tutorial at [GSAS-II-FindProfParamCW]_ was implimented as a script. Users should collect diffraction data file with a well characterized powder that per the tutorial guidance: "Ideally, one should use a material or mixture of materials that has peaks over the entire range where you collect data and use a material(s) that have negligible sample broadening (from crystallite size or microstrain). The NIST LaB6 standards (SRM 660, 660a and 660b) are good choices for this, as they have very little sample broadening and a relatively small number of peaks but over a wide angular range, although it would be good to have peaks starting somewhat lower in 2theta."  


=========================
Expected Output
=========================


=========================
References
=========================
.. Using Zotero Quick Copy and Chicago Manual of Style 17th edition (author-date)
    Remove all spaces and replace with hyphens
    Place in alphabetical order

.. [GSAS-2004] Larson, Allen C, and Robert B Von Dreele. 2004. “GSAS - General Structure Analysis System.” LAUR 86-748. Los Alamos National Laboratory.

.. [GSAS-II-FindProfParamCW] Example https://subversion.xray.aps.anl.gov/pyGSAS/Tutorials/CWInstDemo/FindProfParamCW.htm


.. automodule:: user_guide
    :members:
