InstrumentFileCreation
=========================


=========================
Background
=========================

**Under development - Not currently supported**
In the meantime one can use GSAS-II directly [GSAS-II-github]_ and some of the tutorials [GSAS-II-FindProfParamCW]_ to generate a file.

=========================
File Description
=========================

The Instrument Parameter File uses the conventions [GSAS-2004]_. Depending on the type of diffraction setup, there may be differences in the file. The most pronounced differences are in The [GSAS-2004]_ guide gives some examples of the profile functions on pages 143 to 165.

The Instrument Parameter File is readable with a text editor and contains the following items:

Header:
#GSAS-II instrument parameter file; do not add/delete items!

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

=========================
Usage
=========================

**Under development**

The approach following the tutorial at [GSAS-II-FindProfParamCW]_ will be implemented as a script to generate the Instrument Parameter File. Users should collect diffraction data file with a well characterized powder that per the tutorial guidance: "Ideally, one should use a material or mixture of materials that has peaks over the entire range where you collect data and use a material(s) that have negligible sample broadening (from crystallite size or microstrain). The NIST LaB6 standards (SRM 660, 660a and 660b) are good choices for this, as they have very little sample broadening and a relatively small number of peaks but over a wide angular range, although it would be good to have peaks starting somewhat lower in 2theta."


=========================
Expected Output
=========================

**Under development**


