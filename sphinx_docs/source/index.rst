.. AusteniteCalculator documentation master file, created by
   sphinx-quickstart on Sun Dec 26 18:03:57 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

##########################################################
Welcome to the documentation for the AusteniteCalculator!
##########################################################

The Austenite Calculator is designed to provide an estimate of the phase fraction in steel materials and the uncertainty in that estimate separated into several different sources of uncertainty. While the initial implementation and testing has focused on steels, this application should accept any phase information.

##########################################################
User guide and additional documentation
##########################################################

The Austenite Calculator is implemented as a web-based application that can be interacted with via a web browser.   Background for the application (including references), assumptions, and limitations of the application are listed in the :doc:`user_guide`. A walkthrough of the application is listed in the :doc:`overview`.  If users run into issues, please post an issue on GitHub: [Austenite-Calculator-github]_ or contact the developers.

.. toctree::
   :maxdepth: 3

   user_guide

.. toctree::
   :maxdepth: 3
   
   overview

##########################################################
Examples
##########################################################

.. toctree::
   :maxdepth: 1
   
   Example01
   Example02
   
##########################################################
Software and functions used
##########################################################

.. toctree::
   :maxdepth: 1
   :caption: A summary of the data structure of the Austenite Calculator is listed on the following page:
   
   DataStructure
   
.. toctree::
   :maxdepth: 1
   :caption: Documentation of the functions called by the Austenite Calculator are listed on the following pages:
 
   app
   compute_results
   compute_uncertainties
   fit

.. toctree::
   :maxdepth: 1
   :caption: In addition to the X-Ray Diffraction File(s) and the Crystallographic Information Files (.cif), two additional files are needed to analyze the XRD data: an Instrument Parameter File (.instprm) and a Crystallites Illuminated JSON File (.json). A description of these files and how to create them are listed on the following pages:
   
   InstrumentFileCreation
   CrystallitesIlluminatedFileCreation


==========================================
Indices and tables
==========================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


##########################################################
History & License
##########################################################

==========================================
Release History
==========================================
* 0.1.0 Alpha release


==========================================
Change Log
==========================================


==========================================
License
==========================================

This data/work was created by employees of the National Institute of Standards and Technology (NIST), an agency of the Federal Government. Pursuant to title 17 United States Code Section 105, works of NIST employees are not subject to copyright protection in the United States.  This data/work may be subject to foreign copyright.

The data/work is provided by NIST as a public service and is expressly provided “AS IS.” NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST does not warrant or make any representations regarding the use of the data or the results thereof, including but not limited to the correctness, accuracy, reliability or usefulness of the data. NIST SHALL NOT BE LIABLE AND YOU HEREBY RELEASE NIST FROM LIABILITY FOR ANY INDIRECT, CONSEQUENTIAL, SPECIAL, OR INCIDENTAL DAMAGES (INCLUDING DAMAGES FOR LOSS OF BUSINESS PROFITS, BUSINESS INTERRUPTION, LOSS OF BUSINESS INFORMATION, AND THE LIKE), WHETHER ARISING IN TORT, CONTRACT, OR OTHERWISE, ARISING FROM OR RELATING TO THE DATA (OR THE USE OF OR INABILITY TO USE THIS DATA), EVEN IF NIST HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

To the extent that NIST may hold copyright in countries other than the United States, you are hereby granted the non-exclusive irrevocable and unconditional right to print, publish, prepare derivative works and distribute the NIST data, in any medium, or authorize others to do so on your behalf, on a royalty-free basis throughout the world.

You may improve, modify, and create derivative works of the data or any portion of the data, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the data and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the data:  Data citation recommendations are provided at https://www.nist.gov/open/license.

Permission to use this data is contingent upon your acceptance of the terms of this agreement and upon your providing appropriate acknowledgments of NIST’s creation of the data/work.

==========================================
Disclaimer
==========================================

Certain equipment, instruments, software, or materials are identified in this document in order to specify the experimental procedure adequately. Such identification is not intended to imply recommendation or endorsement of any product or service by NIST, nor is it intended to imply that the materials or equipment identified are necessarily the best available for the purpose.
