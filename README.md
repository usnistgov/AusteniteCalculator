# AusteniteCalculator



follow format from Library?
https://inet.nist.gov/announcement/readme
I thought there was one for GitHub too...

## Files needed

Mandatory files:
- Diffraction data files.  .xrdml is one type, and user may have more than one file.  I don’t want to necessarily work with multiple files right now, but I do want to keep that possibility open in design.
- Phase description files.  These are the .cif files.  Right now there’s just two, but I’d like to again leave it open for more.  

Kind of mandatory until we sort out a better solution:
- Instrument parameter data file.  Ideally I’d like to have users import a calibration file and have GSAS-II generate this.  In the GUI this is optional since it will generate a default instrument parameter file if none is provided.  But with the scripting toolkit, it doesn’t generate a default option right now.


## Example data

Data from L210209-MRC-001
- Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper power.xrdml

Used inital data to create calibration file 'TestCalibration.instprm'
- Not a recommended method...

### CIF files
These are files that describe the lattice information and composition information

Two files are included for each phase, austenite and ferrite.
Duplex steel (B160506-AAC-001), composition from E160629-AAC-004.
Bulk composition used for each, no alloying segregation by phase calculated.
- austenite-Duplex.cif
- ferrite-Duplex.cif

