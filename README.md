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
- 0.0.0 Development

## Author Information

Name: Adam Creuziger
Institution: National Institute of Standards and Technology
Address: 100 Bureau Drive, Gaithersburg, MD 20899
Email: adam.creuziger@nist.gov

## Funding sources that supported the collection and analysis of the data:

Support for Adam Creuziger was provided by the National Institute of Standards and Technology (NIST), an agency of the Federal Government.


# SHARING/ACCESS INFORMATION

## How to run the application

We plan to eventually deploy the Austenite Calculator as a web application. For now, one may run the application using [Docker](https://www.docker.com/), or alternatively one can run the application locally from a custom conda enviroment using the provided [yml file](conda_gsas_env.yml). Specific instructions for both options are below. To deploy a volume in docker, which enables interaction with the files created by the application, first create a volume (`docker volume create [name of volume]`) and then run the container mounted in said volume (`docker run -d \ --name [name] \ --mount source=[volume name],target=[target directory]`).

### Locally

To run the file locally, first download the AusteniteCalculator repository (click 'Code' and then 'Download ZIP' at [the main repository page](https://github.com/usnistgov/AusteniteCalculator)). Then, build a GSAS conda environment using the following command (using a terminal with the working directory set to the main directory of the AusteniteCalculator project). This may take several minutes.
```
conda env create -f conda_gsas_env.yml
```
Then, activate the environment with 
```
conda activate gsas
```
Finally, navigate your terminal to the AusteniteCalculator/app/ folder, and then run
```
python app.py
```
to start the flask server. The application should then be visible at localhost:8050. 


### From a Docker Container

To run the application using Docker you will first need to install Docker (installation instructions can be found [here](https://docs.docker.com/get-docker/)). Once Docker is installed, download the AusteniteCalculator repository (click 'Code' and then 'Download ZIP' at [the main repository page](https://github.com/usnistgov/AusteniteCalculator)). After decompressing the file, navigate your terminal to the main directory of the project (the same level as Dockerfile). Then, run the following command to build the image:
```
docker build -t austenite_calculator .
```
This installs all necessary software (GSAS-II, python libraries, etc.) into a Unix environment.

To run the container, run the following command:
```
docker run -d -p 8080:8050 --name my_container austenite_calculator
```
(-d for 'detached', -p specifies the port mapping, '--name' gives a name to the running container, and 'austenite_calculator' tells Docker which image to build the container from.) Then the app should be visible at `localhost:8080` (accessed via your web browser).  

To stop and remove the running container, run the following:
```
docker rm -f my_container
```
If you wish to run the container again, note that you do not need to run `docker build` again (unless you change the Dockerfile). You can simply run the `docker run` command.

Alternatively, you can run, stop, and remove the container using the Docker Desktop application. For more instructions on using Docker, see the official guide [here](https://docs.docker.com/get-started/).

## Licence
See [license.md](license.md).

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

Many of these entries use data IDs developed in the NIST Center for Automotive Lightweighting (NCAL).  They are retained to provide additional data provenance information.

### Diffraction data files

| Filename | Data ID | Acquired by | Format | Description |
| -------- | ------ | ---- |---- | ---- |
| E211110-AAC-001_005-000_exported.csv | E211110-AAC-001 | Adam Creuziger | csv | LaB6 calibration sample |
| E211110-AAC-001_008-000_exported.csv | E211110-AAC-001 | Adam Creuziger | csv | Fe LSS0411-23, 99.5% purity Fe powder in epoxy matrix. Powder was mesh size 325 (44 um), epoxy matrix density approximately 15% lower than loose powder. |
| E211110-AAC-001_012-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | 316L LSS0312-01, 316L powder in epoxy matrix. Composition given as Fe:Cr:Ni:Mo 67.5:17:13:2.5 (units unclear). Powder was mesh size 325 (44 um), epoxy matrix density approximately 15% lower than loose powder.|
| E211110-AAC-001_013-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | RA 0311-14, retained austenite reference material with pure Fe and 316L powder in epoxy matrix. Powder was mesh size 325 (44 um), epoxy matrix density approximately 15% lower than loose powder. Nominal phase fraction of 11.94% ± 2% |
| E211110-AAC-001_014-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | Normal direction (phi=0, chi=0) data of a Duplex steel sample S170606-RAU-007 |
| E211110-AAC-001_015-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | (phi=0, chi=30) data of a Duplex steel sample S170606-RAU-007 |
| E211110-AAC-001_016-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | (phi=60, chi=30) data of a Duplex steel sample S170606-RAU-007 |
| E211110-AAC-001_017-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | (phi=30, chi=54) data of a Duplex steel sample S170606-RAU-007 |
| E211110-AAC-001_018-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | (phi=90, chi=54) data of a Duplex steel sample S170606-RAU-007 |



### CIF files
These are files that describe the lattice information and composition information. Two files are likely needed for each phase, an austenite and ferrite phase.

| Filename | Created by | Description |
| -------- |  ---- | ---- |
| austenite-Duplex.cif | Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Bulk composition used for each phase, no alloying segregation by phase calculated. Source for lattice parameters? Source for Uiso?|
| ferrite-Duplex.cif| Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Bulk composition used for each phase, no alloying segregation by phase calculated. Source for lattice parameters? Source for Uiso?|
| ferrite-PureFe.cif | Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Uses lattice parameters and Uiso from ferrite-Duplex.cif|


### Instrument calibration files

| Filename |Instrument| Created by | Description |
| -------- | ------ | ---- | ---- |
| TestCalibration.instprm | Mines Empyrean | Adam Creuziger | Used Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper power.xrdml data to create calibration file. Not a recommended method, place holder for now.  |
|BrukerD8_E211110.instprm| NIST MML Bruker D8 | Adam Creuziger | Used process from part 1 of https://subversion.xray.aps.anl.gov/pyGSAS/Tutorials/CWInstDemo/FindProfParamCW.htm and E211110-AAC-001_005-000_exported.csv as the data set. |

## Example Data Folders
In the ExampleData folder, several subfolders have been made with collected example files.
## Example01

Example data from a duplex steel ND direction, courtesy of Michael Cox.

| Filename | Data ID | Acquired by | Format | Description |
| -------- | ------ | ---- |---- | ---- |
| Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper power.xrdml | L210209-MRC-001 | Michael Cox | XRDML| Normal direction (phi=0, chi=0) data of a Duplex steel (B160506-AAC-001) |


| Filename |Instrument| Created by | Description |
| -------- | ------ | ---- | ---- |
| TestCalibration.instprm | Mines Empyrean | Adam Creuziger | Used Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper power.xrdml data to create calibration file. Not a recommended method, place holder for now.  |

### CIF files
These are files that describe the lattice information and composition information. Two files are likely needed for each phase, an austenite and ferrite phase.

| Filename | Created by | Description |
| -------- |  ---- | ---- |
| austenite-Duplex.cif | Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Bulk composition used for each phase, no alloying segregation by phase calculated. Source for lattice parameters? Source for Uiso?|
| ferrite-Duplex.cif| Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Bulk composition used for each phase, no alloying segregation by phase calculated. Source for lattice parameters? Source for Uiso?|


## Example02

Example data from a duplex steel, courtesy of Michael Cox.

| Filename | Data ID | Acquired by | Format | Description |
| -------- | ------ | ---- |---- | ---- |
| Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper power.xrdml | L210209-MRC-001 | Michael Cox | XRDML| Normal direction (phi=0, chi=0) data of a Duplex steel (B160506-AAC-001) |
| Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Duplex_10b_I8_Angles_30_54.xrdml | L210209-MRC-001 | Michael Cox | XRDML| phi=30, chi=54 data of a Duplex steel (B160506-AAC-001)|
| Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Duplex_10b_I6_Angles_60_30.xrdml | L210209-MRC-001 | Michael Cox | XRDML| phi=60, chi=30 data of a Duplex steel (B160506-AAC-001)|
| Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Duplex_10b_I4_Angles_0_30.xrdml | L210209-MRC-001 | Michael Cox |  XRDML|phi=0, chi=30 data of a Duplex steel (B160506-AAC-001)|
| Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Duplex_10b_I2_Angles_90_54_1.xrdml | L210209-MRC-001 | Michael Cox |  XRDML|phi=90, chi=54 data of a Duplex steel (B160506-AAC-001)|

| Filename |Instrument| Created by | Description |
| -------- | ------ | ---- | ---- |
| TestCalibration.instprm | Mines Empyrean | Adam Creuziger | Used Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper power.xrdml data to create calibration file. Not a recommended method, place holder for now.  |

### CIF files
These are files that describe the lattice information and composition information. Two files are likely needed for each phase, an austenite and ferrite phase.

| Filename | Created by | Description |
| -------- |  ---- | ---- |
| austenite-Duplex.cif | Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Bulk composition used for each phase, no alloying segregation by phase calculated. Source for lattice parameters? Source for Uiso?|
| ferrite-Duplex.cif| Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Bulk composition used for each phase, no alloying segregation by phase calculated. Source for lattice parameters? Source for Uiso?|

## Example03

Example data from a duplex steel, courtesy of Adam Creuziger.

#### Data files
| Filename | Data ID | Acquired by | Format | Description |
| -------- | ------ | ---- |---- | ----
| E211110-AAC-001_014-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | Normal direction (phi=0, chi=0) data of a Duplex steel sample S170606-RAU-007 |
| E211110-AAC-001_015-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | (phi=0, chi=30) data of a Duplex steel sample S170606-RAU-007 |
| E211110-AAC-001_016-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | (phi=60, chi=30) data of a Duplex steel sample S170606-RAU-007 |
| E211110-AAC-001_017-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | (phi=30, chi=54) data of a Duplex steel sample S170606-RAU-007 |
| E211110-AAC-001_018-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | (phi=90, chi=54) data of a Duplex steel sample S170606-RAU-007 |

#### Instrument calibration files

| Filename |Instrument| Created by | Description |
| -------- | ------ | ---- | ---- |
|BrukerD8_E211110.instprm| NIST MML Bruker D8 | Adam Creuziger | Used process from part 1 of https://subversion.xray.aps.anl.gov/pyGSAS/Tutorials/CWInstDemo/FindProfParamCW.htm and E211110-AAC-001_005-000_exported.csv as the data set. |

#### CIF files
These are files that describe the lattice information and composition information. Two files are likely needed for each phase, an austenite and ferrite phase.

| Filename | Created by | Description |
| -------- |  ---- | ---- |
| austenite-Duplex.cif | Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Bulk composition used for each phase, no alloying segregation by phase calculated. Source for lattice parameters? Source for Uiso?|
| ferrite-Duplex.cif| Adam Creuziger | Duplex steel (B160506-AAC-001), composition from E160629-AAC-004. Bulk composition used for each phase, no alloying segregation by phase calculated. Source for lattice parameters? Source for Uiso?|

## Example04
Retained austenite reference material produced by an external vendor by combining a ferritic and austenitic powder.  Data set includes measurements of each powder as well.

#### Data files
| Filename | Data ID | Acquired by | Format | Description |
| -------- | ------ | ---- |---- | ---- |
| E211110-AAC-001_005-000_exported.csv | E211110-AAC-001 | Adam Creuziger | csv | LaB6 calibration sample |
| E211110-AAC-001_008-000_exported.csv | E211110-AAC-001 | Adam Creuziger | csv | Fe LSS0411-23, 99.5% purity Fe powder in epoxy matrix. Powder was mesh size 325 (44 um), epoxy matrix density approximately 15% lower than loose powder. |
| E211110-AAC-001_012-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | 316L LSS0312-01, 316L powder in epoxy matrix. Composition given as Fe:Cr:Ni:Mo 67.5:17:13:2.5 (units unclear). Powder was mesh size 325 (44 um), epoxy matrix density approximately 15% lower than loose powder.|
| E211110-AAC-001_013-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | RA 0311-14, retained austenite reference material with pure Fe and 316L powder in epoxy matrix. Powder was mesh size 325 (44 um), epoxy matrix density approximately 15% lower than loose powder. Nominal phase fraction of 11.94% ± 2% |

#### CIF files
These are files that describe the lattice information and composition information. Two files are likely needed for each phase, an austenite and ferrite phase.

| Filename | Created by | Description |
| -------- |  ---- | ---- |

TO DO

#### Instrument calibration files

| Filename |Instrument| Created by | Description |
| -------- | ------ | ---- | ---- |
|BrukerD8_E211110.instprm| NIST MML Bruker D8 | Adam Creuziger | Used process from part 1 of https://subversion.xray.aps.anl.gov/pyGSAS/Tutorials/CWInstDemo/FindProfParamCW.htm and E211110-AAC-001_005-000_exported.csv as the data set. |


## Example05
NIST Standard Reference Material 487 (withdrawn).

#### Data files
| Filename | Data ID | Acquired by | Format | Description |
| -------- | ------ | ---- |---- | ---- |
| E211110-AAC-001_019-000_exported.csv| E211110-AAC-001 | Adam Creuziger | csv | SRM 487-157, NIST retained austenite SRM 487 (withdrawn). Expected to contain 30% austenite.  More information is available at https://doi.org/10.6028/NBS.SP.260-78 |

#### CIF files
These are files that describe the lattice information and composition information. Two files are likely needed for each phase, an austenite and ferrite phase.

| Filename | Created by | Description |
| -------- |  ---- | ---- |
| austenite-SRM487.cif | Adam Creuziger | 310 Stainless Steel, composition from NBS SP 260-78. Lattice parameters fit from datafile. Source for Uiso?|
| austenite-SRM487-high.cif | Caleb Schenck | 310 Stainless Steel, composition from https://www.theworldmaterial.com/aisi-310-stainless-steel/. Lattice parameters fit from datafile. Source for Uiso?|
| austenite-SRM487-low.cif | Caleb Schenck | 310 Stainless Steel, composition from https://www.theworldmaterial.com/aisi-310-stainless-steel/. Lattice parameters fit from datafile. Source for Uiso?|
| ferrite-SRM487.cif| Adam Creuziger | 430 Stainless Steel, composition from NBS SP 260-78. Lattice parameters fit from datafile. Source for Uiso?|
| ferrite-SRM487-high.cif| Caleb Schenck | 430 Stainless Steel, composition from https://www.theworldmaterial.com/astm-aisi-430-grade-stainless-steel/. Lattice parameters fit from datafile. Source for Uiso?|
| ferrite-SRM487-low.cif| Caleb Schenck | 430 Stainless Steel, composition from https://www.theworldmaterial.com/astm-aisi-430-grade-stainless-steel/. Lattice parameters fit from datafile. Source for Uiso?|

#### Instrument calibration files

| Filename |Instrument| Created by | Description |
| -------- | ------ | ---- | ---- |
|BrukerD8_E211110.instprm| NIST MML Bruker D8 | Adam Creuziger | Used process from part 1 of https://subversion.xray.aps.anl.gov/pyGSAS/Tutorials/CWInstDemo/FindProfParamCW.htm and E211110-AAC-001_005-000_exported.csv as the data set. |


# METHODOLOGICAL INFORMATION

None at this time

# BIBLIOGRAPHY

[1]  Toby, B. H., & Von Dreele, R. B. (2013). "GSAS-II: the genesis of a modern open-source all purpose crystallography software package". Journal of Applied Crystallography, 46(2), 544-549. ​doi:10.1107/S0021889813003531
