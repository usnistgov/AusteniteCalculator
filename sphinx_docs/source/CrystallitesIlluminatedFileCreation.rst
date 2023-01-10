CrystallitesIlluminatedFileCreation
=======================================


=========================
Background
=========================
In addition to the X-Ray Diffraction File(s) and the Crystallographic Information Files (.cif), two additional files are needed to analyze the XRD data: an Instrument Parameter File (.instprm) and a Crystallites Illuminated JSON File (.json).


=========================
File Description
=========================
The Crystallites Illuminated JSON file contains information about the phases.  JSON file format uses attribute-value pairs to encode data.

Four pieces of information are for each phase:
 - The .cif filename for phase.
 - The powder size in micrometers (um).
 - The number of crystallites per particle.
 - Rocking angle of a crystal (degrees).

For each phase, the attribute is the .cif file name, and the value is a comma delimited list of the powder size and number of crystallites enclosed in square brackets.

Examples:
 - "austenite-Duplex.cif": "[50,10]",
 - "ferrite-Duplex.cif": "[50,10]",
    
In addition, details of the xray diffractometer geometry are needed.  While this is sometimes encoded in the x-ray diffraction file, parsing this information can be difficult. The nomenclature and definitions from [Alexander-1948]_ were used in this work

Eight pieces of information are needed:
 - beam_shape: Shape of the aperature of the incident x-ray. Options are "square" and "circle"
 - beam_size: Size of the aperature (mm). Diameter for circular beams, edge length for square beams. Currently does not account for beam divergence.
 - raster_x: Oscillation length in the diffractometer x direction (mm). If the sample is oscillated at a rate signficantly greater than the scan increment, the raster area defines the illuminated volume instead of the beam_size.
 - raster_y: Oscillation length in the diffractometer y direction (mm). If the sample is oscillated at a rate signficantly greater than the scan increment, the raster area defines the illuminated volume instead of the beam_size.
 - L: Sample to x-ray source distance (mm).  Currently assumes that the sample to detector distance is equivalent.
 - W_F: Apparent width of the x-ray tube focus (mm). As these are often described as the slit width, they should be the same or similar to the the beam_size dimension.
 - H_F: Height of the x-ray tube focus (mm). As these are often described as the slit height, they should be the same or similar to the the beam_size dimension.
 - H_R: The smallest of either the height of the receiving slit or detector window (mm). For 2D detectors, H_R can often be calculated from the gamma term via the equation gamma*L=H_R/L.


Example for a lab based system:
    "beam_shape": "square",
    "beam_size": "1",
    "raster_x": "4",
    "raster_y": "4",
    "L": "265",
    "W_F": "1",
    "H_F": "1",
    "H_R": "70"


Example for a synchrotron based system:
    "beam_shape": "square",
    "beam_size": "0.2",
    "raster_x": "0",
    "raster_y": "0",
    "L": "20000",
    "W_F": "0.2",
    "H_F": "0.2",
    "H_R": "1000"



=========================
Usage
=========================

For polycrystalline materials, the

The name is used to match the phases, so it is important that this string matches the name of the file.


- The powder size in micrometers (um).

Reasonable values for number of crystallites per particle:
- 1 for polycrystalline materials
- between 10 and 100 for powders

Reasonable values for the rocking angle of a crystal [Alexander-1948]_.
- Ideally perfect crystal  (0.0025 deg = 9 seconds of an arc)
- Undeformed crystals (0.25 deg = 15 minues of an arc)
- Deformed crystals (1 deg to 5 deg increasing as level of deformation increases)


[Alexander-1948]_ assumes:
- H (heights) are perpendicular to the source-sample-detector plane
- W (widths) are parallel to the source-sample-detector plane
- _F is the source
- _R is the detector (reciever)

=========================
Expected Output
=========================


=========================
References
=========================
.. Using Zotero Quick Copy and Chicago Manual of Style 17th edition (author-date)
    Remove all spaces and replace with hyphens
    Place in alphabetical order

.. [Alexander-1948] Alexander, Leroy, Harold P. Klug, and Elizabeth Kummer. 1948. “Statistical Factors Affecting the Intensity of X‐Rays Diffracted by Crystalline Powders.” Journal of Applied Physics 19 (8): 742–53. https://doi.org/10.1063/1.1698200.


.. automodule:: user_guide
    :members:
