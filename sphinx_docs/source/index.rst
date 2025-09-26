.. AusteniteCalculator documentation master file, created by
   sphinx-quickstart on Sun Dec 26 18:03:57 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the documentation for the AusteniteCalculator!
##########################################################

The Austenite Calculator is designed to provide an estimate of the phase fraction in steel materials and the uncertainty in that estimate. While the initial implimentation and testing has focused on steels, this application should accept any phase information.


==========================================
Release History
==========================================
* In development, not yet officially released.


==========================================
Change Log
==========================================

==========================================
Software and functions used
==========================================

The code for the Austenite Calculator is available on GitHub: [Austenite-Calculator-github]_.  This software builds on the GSAS-II diffraction analysis package [Toby-2013]_ [GSAS-II-github]_, using the *GSASIIscriptable* module. JavaScript is used to render the plots, and Docker is used as a container.

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
   :caption: Some additional files are required to run the application.  A description of these files and how to create them are listed on the following pages:

   CrystallitesIlluminatedFileCreation
   InstrumentFileCreation

==========================================
User guide and additional documentation
==========================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:
 
   user_guide
   DataStructure
   app
   compute_results
   compute_uncertainties
   fit


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

License
==================



This data/work was created by employees of the National Institute of Standards and Technology (NIST), an agency of the Federal Government. Pursuant to title 17 United States Code Section 105, works of NIST employees are not subject to copyright protection in the United States.  This data/work may be subject to foreign copyright.

The data/work is provided by NIST as a public service and is expressly provided “AS IS.” NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST does not warrant or make any representations regarding the use of the data or the results thereof, including but not limited to the correctness, accuracy, reliability or usefulness of the data. NIST SHALL NOT BE LIABLE AND YOU HEREBY RELEASE NIST FROM LIABILITY FOR ANY INDIRECT, CONSEQUENTIAL, SPECIAL, OR INCIDENTAL DAMAGES (INCLUDING DAMAGES FOR LOSS OF BUSINESS PROFITS, BUSINESS INTERRUPTION, LOSS OF BUSINESS INFORMATION, AND THE LIKE), WHETHER ARISING IN TORT, CONTRACT, OR OTHERWISE, ARISING FROM OR RELATING TO THE DATA (OR THE USE OF OR INABILITY TO USE THIS DATA), EVEN IF NIST HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

To the extent that NIST may hold copyright in countries other than the United States, you are hereby granted the non-exclusive irrevocable and unconditional right to print, publish, prepare derivative works and distribute the NIST data, in any medium, or authorize others to do so on your behalf, on a royalty-free basis throughout the world.

You may improve, modify, and create derivative works of the data or any portion of the data, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the data and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the data:  Data citation recommendations are provided at https://www.nist.gov/open/license.

Permission to use this data is contingent upon your acceptance of the terms of this agreement and upon your providing appropriate acknowledgments of NIST’s creation of the data/work.
