# AusteniteCalculator

This project is still in development.  When completed, we hope to have a robust method to determine the phase fraction of austenite in steels with metrics on the uncertainties and recommendations on methods to reduce the uncertainty.  


## Readme developed from NIST Readme Template

# Sections
- GENERAL INFORMATION
- SHARING/ACCESS INFORMATION
- DATA & FILE OVERVIEW
- METHODOLOGICAL INFORMATION
- BIBLIOGRAPHY


# GENERAL INFORMATION

## Version History
- 1.0.0 Initial Release

## Author Information

Name: Adam Creuziger 
Institution: National Institute of Standards and Technology 
Address: 100 Bureau Drive, Gaithersburg, MD 20899 
Email: adam.creuziger@nist.gov

## Funding sources that supported the collection and analysis of the data: 

Support for Adam Creuziger was provided by the National Institute of Standards and Technology (NIST), an agency of the Federal Government.


# SHARING/ACCESS INFORMATION

## Licence
See license.md

## Disclaimers
The data/work is provided by NIST as a public service and is expressly provided “AS IS.” NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST does not warrant or make any representations regarding the use of the data or the results thereof, including but not limited to the correctness, accuracy, reliability or usefulness of the data. NIST SHALL NOT BE LIABLE AND YOU HEREBY RELEASE NIST FROM LIABILITY FOR ANY INDIRECT, CONSEQUENTIAL, SPECIAL, OR INCIDENTAL DAMAGES (INCLUDING DAMAGES FOR LOSS OF BUSINESS PROFITS, BUSINESS INTERRUPTION, LOSS OF BUSINESS INFORMATION, AND THE LIKE), WHETHER ARISING IN TORT, CONTRACT, OR OTHERWISE, ARISING FROM OR RELATING TO THE DATA (OR THE USE OF OR INABILITY TO USE THIS DATA), EVEN IF NIST HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

## Are there any restrictions or guidelines on how to use the data? 
None currently set.

## Citation Guidance
None currently set.

# DATA & FILE OVERVIEW
## Files needed

Mandatory files:
- Diffraction data files.  .xrdml is one type, and user may have more than one file.  Currently only a single file is supported but I do want to keep that possibility open in design.
- Phase description files.  These are the .cif files.  Currently only two files are supported, but I’d like to again leave it open for more.  

Kind of mandatory until we sort out a better solution:
- Instrument parameter data file.  Ideally users will import a calibration file and have GSAS-II [1] generate this.  

## Example data

Data from L210209-MRC-001
- Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper power.xrdml

Used inital data to create calibration file 'TestCalibration.instprm'
- Not a recommended method, place holder for now

### CIF files
These are files that describe the lattice information and composition information

Two files are included for each phase, austenite and ferrite.
Duplex steel (B160506-AAC-001), composition from E160629-AAC-004.
Bulk composition used for each, no alloying segregation by phase calculated.
- austenite-Duplex.cif
- ferrite-Duplex.cif

# METHODOLOGICAL INFORMATION

None at this time

# BIBLIOGRAPHY

[1]  Toby, B. H., & Von Dreele, R. B. (2013). "GSAS-II: the genesis of a modern open-source all purpose crystallography software package". Journal of Applied Crystallography, 46(2), 544-549. ​doi:10.1107/S0021889813003531
